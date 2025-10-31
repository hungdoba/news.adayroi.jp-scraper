"""
Main entry point for the news scraper application.

This module provides a CLI interface for running the news processing pipeline
and individual pipeline steps.
"""
import sys
import argparse
from pipeline import NewsPipeline
from logging_config import get_logger

logger = get_logger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="News Scraper for Adayroi.jp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                         # Run full pipeline
  python main.py --skip-obsidian         # Run pipeline without opening Obsidian
  python main.py --step scrape           # Run only scraping step
  python main.py --step clean            # Clean data directories
  python main.py --step cleanup          # Cleanup Next.js files
        """
    )

    parser.add_argument(
        "--step",
        choices=[
            "scrape", "group", "merge", "convert", "translate",
            "images", "obsidian", "copy", "deploy", "clean", "cleanup"
        ],
        help="Run a specific pipeline step instead of the full pipeline"
    )

    parser.add_argument(
        "--input",
        help="Input file for specific steps (e.g., JSON file for grouping)"
    )

    parser.add_argument(
        "--output",
        help="Output directory for specific steps"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )

    parser.add_argument(
        "--skip-obsidian",
        action="store_true",
        help="Skip opening Obsidian during the pipeline (useful for automated runs)"
    )

    return parser


def run_specific_step(pipeline: NewsPipeline, step: str, input_file: str | None = None, output_dir: str | None = None) -> None:
    """Run a specific pipeline step."""
    logger.info(f"Running specific step: {step}")

    try:
        if step == "clean":
            pipeline.step_0_clean()

        elif step == "scrape":
            result = pipeline.step_1_scrape_news_feed()
            if result:
                logger.info(f"Scraping completed. Output: {result}")
            else:
                logger.info("No new articles found")

        elif step == "group":
            if not input_file:
                logger.error("Input file required for grouping step")
                return
            result = pipeline.step_2_group_articles(input_file)
            if result:
                logger.info(f"Grouping completed. Output: {result}")

        elif step == "merge":
            if not input_file or not output_dir:
                logger.error(
                    "Input file and output directory required for merge step")
                return
            pipeline.step_3_merge_articles(input_file, output_dir)

        elif step == "convert":
            input_dir = input_file or pipeline.config.dir_step_3
            output_dir = output_dir or pipeline.config.dir_step_4
            pipeline.step_4_convert_html_to_markdown(input_dir, output_dir)

        elif step == "translate":
            input_dir = input_file or pipeline.config.dir_step_4
            output_dir = output_dir or pipeline.config.dir_step_5
            pipeline.step_5_translate_markdown(input_dir, output_dir)

        elif step == "images":
            input_dir = input_file or pipeline.config.dir_step_5
            pipeline.step_6_download_images(input_dir)

        elif step == "obsidian":
            pipeline.step_7_open_obsidian()

        elif step == "copy":
            pipeline.step_8_copy_to_nextjs()

        elif step == "cleanup":
            pipeline.step_9_cleanup_nextjs()

        elif step == "deploy":
            pipeline.step_10_deploy()

        else:
            logger.error(f"Unknown step: {step}")

    except Exception as e:
        logger.error(f"Error running step {step}: {str(e)}", exc_info=True)
        raise


def main() -> None:
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Setup logging with specified level
    from logging_config import setup_logging
    setup_logging(level=args.log_level, log_file="logs/scraper.log")

    logger.info("Starting news scraper application")

    try:
        # Initialize pipeline
        pipeline = NewsPipeline()

        # Set skip_obsidian flag if provided
        if hasattr(args, 'skip_obsidian'):
            pipeline.skip_obsidian = args.skip_obsidian

        if args.step:
            # Run specific step
            run_specific_step(pipeline, args.step, args.input, args.output)
        else:
            # Run full pipeline
            pipeline.run_full_pipeline()

        logger.info("Application completed successfully")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
