from core.image import extract_image_urls
import string
import shutil
import random
import codecs
import json
import os
import re
import datetime
import logging
logger = logging.getLogger(__name__)


def sanitize_yaml_value(value):
    if not isinstance(value, str):
        return value

    # Remove or replace characters that can cause YAML parsing issues
    sanitized = value

    # Replace quotes that might break YAML syntax
    sanitized = sanitized.replace('"', "'")

    # Remove control characters
    sanitized = ''.join(c for c in sanitized if ord(c)
                        >= 32 or c == '\n' or c == '\t')

    # Remove YAML special characters that could cause parsing issues
    for char in [':', '{', '}', '[', ']', '&', '*', '!', '|', '>', '<', '%', '#', '`']:
        sanitized = sanitized.replace(char, '')

    # Trim leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def merge_html_file(html_files, output_folder, title_content):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    random_suffix = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=34))
    output_file = os.path.join(output_folder, f"merged{random_suffix}.html")

    merged_content = []
    for html_file in html_files:
        if not os.path.exists(html_file):
            logger.warning(f"File {html_file} not found, skipping...")
            continue

        with codecs.open(html_file, 'r', encoding='utf-8') as f:
            merged_content.append(f.read())

    merged_html_content = "".join(merged_content)

    for i in range(5, 0, -1):
        merged_html_content = merged_html_content.replace(
            f"<h{i}>", f"<h{i+1}>").replace(f"</h{i}>", f"</h{i+1}>")

    final_html = f"""
    <article>
    <h1>{title_content}</h1>
    {merged_html_content}
    </article>
    """

    with codecs.open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

    return output_file


def append_thumbnail_to_html(html_file, thumbnail_path):
    with codecs.open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_content = f"<img src='{thumbnail_path}'>\n{html_content}"

    with codecs.open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def update_group_ids_to_raw_id(raw_html_path, groups_path):
    with open(groups_path, 'r', encoding='utf-8') as f:
        groups = json.load(f)
    with open(raw_html_path, 'r', encoding='utf-8') as f:
        raw_html = json.load(f)

    id_to_raw_id = {item['id']: item['raw_id'] for item in raw_html}
    id_to_thumbnail = {item['id']: item['thumbnail'] for item in raw_html}

    for group in groups:
        group['thumbnail'] = id_to_thumbnail.get(group['id'][0], "")
        group['id'] = [id_to_raw_id.get(article_id, article_id)
                       for article_id in group['id']]

    with open(groups_path, 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)


def copy_to_nextjs(input_folder: str, nextjs_folder: str):
    # Regular expression to find "used: true" in frontmatter
    used_pattern = re.compile(r'---\s*.*?use\s*:\s*true.*?---', re.DOTALL)

    # Setup paths
    nextjs_markdown_folder = os.path.join(nextjs_folder, 'content')
    nextjs_images_folder = os.path.join(nextjs_folder, 'public')

    # Counters
    total_files = 0
    copied_files = 0

    # Walk through all markdown files in the input directory
    for root, _, files in os.walk(input_folder):
        for file in files:
            if not file.endswith('.md'):
                continue

            total_files += 1
            markdown_file_path = os.path.join(root, file)
            thumbnail_file_path = os.path.join(
                root, 'images', file.replace('.md', '.webp'))

            # Check if the file has used = true
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                if not used_pattern.search(f.read()):
                    continue

            copied_files += 1
            rel_path = os.path.relpath(markdown_file_path, input_folder)
            target_path = os.path.join(nextjs_markdown_folder, rel_path)

            # Copy markdown file
            logger.info(f"Copying {markdown_file_path} to {target_path}")
            shutil.copy2(markdown_file_path, target_path)

            # Copy thumbnail
            target_thumbnail_path = os.path.join(
                nextjs_images_folder,
                os.path.dirname(rel_path),
                'images',
                'thumbnails',
                file.replace('.md', '.webp')
            )

            if os.path.exists(thumbnail_file_path):
                shutil.copy2(thumbnail_file_path, target_thumbnail_path)
            else:
                logger.warning(f"Thumbnail not found: {thumbnail_file_path}")

            # Copy images referenced in markdown
            copy_markdown_images(markdown_file_path, root,
                                 input_folder, nextjs_images_folder, rel_path)

    logger.info(
        f"Copy complete: {copied_files} of {total_files} files copied to {nextjs_folder}")


def copy_markdown_images(markdown_path, root, input_folder, nextjs_images_folder, rel_path):
    images = extract_image_urls(markdown_path)
    for image in images:
        # Remove leading slash if present
        if image.startswith('/'):
            image = image[1:]

        # Try finding the image in the same directory as the markdown
        image_path = os.path.join(root, image)
        if os.path.exists(image_path):
            target_image_path = os.path.join(
                nextjs_images_folder, os.path.dirname(rel_path), image)
            os.makedirs(os.path.dirname(target_image_path), exist_ok=True)
            shutil.copy2(image_path, target_image_path)
            continue

        # Try finding the image from the input folder root
        alt_image_path = os.path.join(input_folder, image)
        if os.path.exists(alt_image_path):
            target_image_path = os.path.join(nextjs_images_folder, image)
            os.makedirs(os.path.dirname(target_image_path), exist_ok=True)
            shutil.copy2(alt_image_path, target_image_path)
            continue

        logger.warning(f"Image not found: {image}")
        logger.info(f"   Tried: {image_path}")
        logger.info(f"   Also tried: {alt_image_path}")


def delete_nextjs_markdown_file(nextjs_folder: str, markdown_filename: str):
    logger.info(
        f"Deleting markdown file: {markdown_filename} from {nextjs_folder}")

    content_folder = os.path.join(nextjs_folder, 'content')
    images_folder = os.path.join(nextjs_folder, 'public')

    markdown_path = None
    for root, _, files in os.walk(content_folder):
        if markdown_filename in files:
            markdown_path = os.path.join(root, markdown_filename)
            break

    if not markdown_path:
        raise FileNotFoundError(
            f"Markdown file {markdown_filename} not found in {content_folder}")

    try:
        thumbnail_path = os.path.join(
            images_folder,
            'images',
            'thubnails',
            markdown_filename.replace('.md', '.webp')
        )

        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            logger.info(f"Deleted thumbnail: {thumbnail_path}")
        else:
            logger.warning(f"Thumbnail not found: {thumbnail_path}")
            # raise FileNotFoundError(
            #     f"Thumbnail not found for {thumbnail_path}")

        images = extract_image_urls(markdown_path)
        for image in images:
            # Remove leading slash if present
            if image.startswith('/'):
                image = image[1:]
            image_path = os.path.join(images_folder, image)

            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted image: {image_path}")
                continue
            else:
                raise FileNotFoundError(
                    f"Image not found in markdown directory: {image_path} | {images_folder}")

        os.remove(markdown_path)
        logger.info(f"Deleted markdown: {markdown_path}")

        return True

    except Exception as e:
        logger.error(f"Error deleting {markdown_filename}: {e}")
        return False


def cleanup_old_markdown_files(project_folder: str):
    """
    Remove markdown files older than one month and their associated images.
    """
    content_folder = os.path.join(project_folder, 'content')

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)

    for root, _, files in os.walk(content_folder):
        for file in files:
            if not file.endswith('.md'):
                continue

            markdown_path = os.path.join(root, file)

            # Read the markdown file to check created_at
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract created_at from frontmatter
            frontmatter_match = re.search(
                r'---\s*(.*?)\s*---', content, re.DOTALL)
            if not frontmatter_match:
                continue

            frontmatter = frontmatter_match.group(1)
            date_match = re.search(
                r'created_at\s*:\s*["\']?(\d{4}-\d{2}-\d{2})', frontmatter)

            if not date_match:
                continue

            created_date = datetime.datetime.strptime(
                date_match.group(1), '%Y-%m-%d')

            # Check if file is older than one month
            if created_date < cutoff_date:
                delete_nextjs_markdown_file(
                    project_folder, file)
