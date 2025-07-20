"""
News processing pipeline orchestrator.
"""
import os
import glob
import json
import shutil
import codecs
import datetime
from pathlib import Path
from typing import Optional, List

from markitdown import MarkItDown

from config import config
from logging_config import get_logger
from core.deploy import build_next_app, git_push_next_app
from core.gemini import group_article, translate_article_list
from core.scraper import fetch_and_save_article, scrape_news_feed
from core.image import delete_remote_images, download_and_replace_images
from utils.log import get_all_ids, log_id
from utils.execute import execute_sequential
from utils.file import (
    append_thumbnail_to_html,
    copy_to_nextjs,
    merge_html_file,
    update_group_ids_to_raw_id,
    cleanup_old_markdown_files
)

logger = get_logger(__name__)


class NewsPipeline:
    """Main pipeline for processing news articles."""

    def __init__(self):
        """Initialize the pipeline with configuration."""
        config.validate()
        self.config = config
        logger.info("News pipeline initialized")

    def run_full_pipeline(self) -> None:
        """Run the complete news processing pipeline."""
        logger.info("Starting full news processing pipeline")

        try:
            # Step 1: Scrape news feed
            news_feed = self.step_1_scrape_news_feed()
            if news_feed is None:
                logger.info("No new articles found. Exiting pipeline.")
                return

            # Step 2: Group articles
            group_articles = self.step_2_group_articles(news_feed)
            if group_articles is None:
                logger.error("Failed to group articles")
                return

            # Step 3: Merge articles
            self.step_3_merge_articles(group_articles, self.config.dir_step_3)

            # Step 4: Convert to markdown
            self.step_4_convert_html_to_markdown(
                self.config.dir_step_3,
                self.config.dir_step_4
            )

            # Step 5: Translate articles
            self.step_5_translate_markdown(
                self.config.dir_step_4,
                self.config.dir_step_5
            )

            # Step 6: Download images
            self.step_6_download_images(self.config.dir_step_5)

            # Step 7: Open Obsidian (optional)
            self.step_7_open_obsidian()

            # Step 8: Copy to Next.js
            self.step_8_copy_to_nextjs()

            # Step 9: Deploy
            self.step_9_deploy()

            logger.info("Full pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise

    def step_0_clean(self) -> None:
        """Clean all data directories."""
        logger.info("Step 0: Cleaning data directories")

        if os.path.exists(self.config.data_dir):
            shutil.rmtree(self.config.data_dir)
            logger.info(f"Deleted directory: {self.config.data_dir}")

    def step_1_scrape_news_feed(self) -> Optional[str]:
        """Scrape news feed, fetch new articles, and save them to JSON."""
        logger.info("Step 1: Starting news feed scraping")

        # Get previously processed article IDs
        processed_ids = get_all_ids(self.config.processed_ids_file)

        # Scrape current news feed
        news_feed_articles = scrape_news_feed(
            self.config.feed_url,
            selector=self.config.news_feed_selector
        )

        # Filter out already processed articles
        new_articles = [
            article for article in news_feed_articles
            if article.raw_id not in processed_ids
        ]

        logger.info(
            f"Found {len(news_feed_articles)} articles, "
            f"{len(new_articles)} are new"
        )

        if not new_articles:
            return None

        # Create output directories
        os.makedirs(self.config.dir_step_1, exist_ok=True)
        os.makedirs(self.config.dir_step_2, exist_ok=True)

        # Fetch content for new articles
        raw_html_data = []
        for article in new_articles:
            log_id(self.config.processed_ids_file, article.raw_id)
            title_content = fetch_and_save_article(
                article.url, article.raw_id, self.config.dir_step_1
            )
            if not title_content:
                logger.warning(f"Failed to fetch article {article.raw_id}")
                continue

            article.title = title_content
            raw_html_data.append(article.__dict__)

        if not raw_html_data:
            return None

        # Save fetched data to JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(
            self.config.dir_step_2,
            f"raw_html_data_{timestamp}.json"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(raw_html_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(raw_html_data)} articles to {filename}")
        return filename

    def step_2_group_articles(self, file_path: str) -> Optional[str]:
        """Group articles using AI."""
        logger.info("Step 2: Starting article grouping")

        groups_json = group_article(file_path=file_path)
        if not groups_json:
            return None

        os.makedirs(self.config.dir_step_2, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.config.dir_step_2,
            f"article_groups_{timestamp}.json"
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            if isinstance(groups_json, str):
                f.write(groups_json)
            else:
                json.dump(groups_json, f, ensure_ascii=False, indent=2)

        update_group_ids_to_raw_id(file_path, output_file)

        logger.info(f"Saved article groups to {output_file}")
        return output_file

    def step_3_merge_articles(self, group_article_filename: str, output_folder: str) -> None:
        """Merge related articles."""
        logger.info("Step 3: Starting article merging")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(group_article_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                ids = item['id']
                if len(ids) == 1:
                    # Single article - just move it
                    old_file = f"{self.config.dir_step_1}/{ids[0]}.html"
                    new_file = old_file.replace("1.raw_html", "3.merged")

                    if not os.path.exists(old_file):
                        logger.warning(
                            f"File {old_file} not found, skipping...")
                        continue

                    shutil.move(old_file, new_file)
                    logger.info(
                        f"Moved single file from {old_file} to {new_file}")
                else:
                    # Multiple articles - merge them
                    title_content = item['title']
                    html_files = [
                        f"{self.config.dir_step_1}/{id}.html" for id in ids]
                    new_file = merge_html_file(
                        html_files, output_folder, title_content)

                    # Delete the original HTML files after merging
                    for id in ids:
                        old_file = f"{self.config.dir_step_1}/{id}.html"
                        if os.path.exists(old_file):
                            os.remove(old_file)
                            logger.debug(f"Deleted original file: {old_file}")

                    logger.info(f"Merged files into {new_file}")

                # Add thumbnail
                thumbnail = item['thumbnail']
                append_thumbnail_to_html(new_file, thumbnail)

    def step_4_convert_html_to_markdown(self, input_folder: str, output_folder: str) -> None:
        """Convert HTML files to Markdown."""
        logger.info("Step 4: Starting HTML to Markdown conversion")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        md = MarkItDown()
        html_files = glob.glob(os.path.join(input_folder, "*.html"))

        for html_file in html_files:
            file_name = os.path.splitext(os.path.basename(html_file))[0]
            output_file = os.path.join(output_folder, f"{file_name}.md")

            markdown_content = md.convert(html_file).markdown

            with codecs.open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.debug(
                f"Converted {os.path.basename(html_file)} to {file_name}.md")

        logger.info(f"Conversion complete. {len(html_files)} files processed")

    def step_5_translate_markdown(self, input_folder: str, output_folder: str) -> None:
        """Translate markdown files."""
        logger.info("Step 5: Starting markdown translation")
        translate_article_list(input_folder, output_folder)

    def step_6_download_images(self, input_folder: str) -> None:
        """Download and process images."""
        logger.info("Step 6: Starting image download")

        files = os.listdir(input_folder)
        for file in files:
            file_path = os.path.join(input_folder, file)
            local_img_md = download_and_replace_images(
                file_path, self.config.dir_step_6)
            delete_remote_images(local_img_md)

    def step_7_open_obsidian(self) -> None:
        """Open Obsidian for content review."""
        logger.info("Step 7: Opening Obsidian")

        def on_completion():
            return "Obsidian operation completed"

        execute_sequential(self.config.obsidian_path, on_completion)

    def step_8_copy_to_nextjs(self) -> None:
        """Copy content to Next.js project."""
        logger.info("Step 8: Copying to Next.js")
        copy_to_nextjs(
            input_folder=self.config.dir_step_8,
            nextjs_folder=self.config.nextjs_dir
        )

    def step_9_deploy(self) -> None:
        """Deploy the Next.js application."""
        logger.info("Step 9: Starting deployment")

        build_success = build_next_app()
        if not build_success:
            logger.error("Failed to build the Next.js app")
            return

        git_push_next_app()
        logger.info("Deployment completed successfully")

    def step_10_cleanup_nextjs(self) -> None:
        """Clean up old markdown files in Next.js project."""
        logger.info("Step 10: Cleaning up Next.js")
        cleanup_old_markdown_files(self.config.nextjs_dir)
        logger.info("Next.js cleanup completed")
