from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
import hashlib
import requests
import re
import os
import logging
logger = logging.getLogger(__name__)


def extract_thumbnail_from_yaml(content):
    yaml_match = re.search(
        r'---\s*.*?thumbnail:\s*["\'](.*?)["\'].*?---', content, re.DOTALL)
    if yaml_match:
        return yaml_match.group(1)
    return ""


def convert_to_webp(
    image_path: str,
    quality: int = 80,
    output_path: str = "",
    lossless: bool = False,
    method: int = 4,
    strip_metadata: bool = True
):
    # Validate input path
    source_path = Path(image_path) if isinstance(
        image_path, str) else image_path
    if not source_path.is_file():
        raise FileNotFoundError(f"Source image does not exist: {source_path}")

    # Validate quality and method
    if not lossless and not 0 <= quality <= 100:
        raise ValueError("Quality must be between 0 and 100")
    if not 0 <= method <= 6:
        raise ValueError("Method must be between 0 and 6")

    # Set output path
    output_path_obj = Path(
        output_path) if output_path else source_path.with_suffix('.webp')

    try:
        with Image.open(source_path) as img:
            # Optimize color mode
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA' if img.getchannel('A') else 'RGB')

            # Strip metadata if requested
            if strip_metadata:
                img.info = {}

            # Save with optimization parameters
            img.save(
                output_path_obj,
                'WEBP',
                quality=quality,
                lossless=lossless,
                method=method,
                exact=True  # Preserve transparency
            )
        return output_path_obj
    except Exception as e:
        return None


def download_and_replace_images(markdown_file_path, output_dir='data/6.images/images'):
    """Download images from a markdown file and replace links with local WebP versions."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read the markdown content
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Process thumbnail
    content = _process_thumbnail(content, output_path, markdown_file_path)

    # Process inline images
    content, replacement_count = _process_inline_images(content, output_path)

    # Write the updated content to a new file
    new_file_path = markdown_file_path.replace('5.translated', '6.images')
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    logger.info(f"Updated markdown saved to {new_file_path}")
    logger.info(f"Downloaded {replacement_count} images")

    return new_file_path


def _process_thumbnail(content, output_path, markdown_file_path):
    """Process thumbnail image from YAML header."""
    thumbnail_url = extract_thumbnail_from_yaml(content)
    if not thumbnail_url:
        return content

    thumbnail_filename = Path(
        output_path) / os.path.basename(markdown_file_path).replace('.md', '.webp')

    try:
        # Download and convert thumbnail
        response = requests.get(thumbnail_url, stream=True, timeout=10)
        response.raise_for_status()

        temp_filename = Path(str(thumbnail_filename).replace('.webp', '.tmp'))
        with open(temp_filename, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)

        webp_path = convert_to_webp(
            str(temp_filename), output_path=thumbnail_filename)

        # Clean up and update content
        if temp_filename.exists():
            temp_filename.unlink()

        if webp_path:
            logger.info(
                f"Downloaded and converted thumbnail to {thumbnail_filename}")
            return re.sub(
                r'(thumbnail:\s*["\']).*?(["\'])',
                r'\1' + str(thumbnail_filename).replace('\\', '/') + r'\2',
                content
            )
    except (requests.RequestException, IOError) as e:
        logger.error(f"Error processing thumbnail: {e}")

    # If we reach here, something failed
    logger.warning(
        "Removing thumbnail URL from content due to download/conversion failure")
    return re.sub(r'(thumbnail:\s*["\']).*?(["\'])', r'\1\2', content)


def _process_inline_images(content, output_path):
    """Process inline images in markdown content."""
    # Regex for both ![alt](url) and <img src="url"> patterns
    image_pattern = re.compile(
        r'!\[.*?\]\((.*?)\)|<img.*?src=[\'\"](.*?)[\'\"].*?>')
    replacements = {}

    # Find and process all matches
    for match in image_pattern.finditer(content):
        image_url = match.group(1) or match.group(2)

        # Skip if already processed or is a local path
        if image_url.startswith(('/', '.', 'data')) or image_url in replacements:
            continue

        try:
            local_path = _download_and_convert_image(image_url, output_path)
            if local_path:
                replacements[image_url] = str(local_path).replace(
                    'data\\6.images', '').replace('\\', '/')
        except Exception as e:
            logger.error(f"Error processing image {image_url}: {e}")
            # Remove the image from content by replacing with empty string
            replacements[image_url] = ''

    # Replace all URLs with local paths
    result = content
    for old_url, new_path in replacements.items():
        result = result.replace(old_url, new_path)

    return result, len(replacements)


def _download_and_convert_image(image_url, output_path):
    """Download image and convert to WebP format."""
    parsed_url = urlparse(image_url)
    original_filename = os.path.basename(parsed_url.path)

    # Add default extension if missing
    if not os.path.splitext(original_filename)[1]:
        original_filename += '.jpg'

    # Create a safe filename by limiting length and using hash for very long names
    max_filename_length = 200  # Leave some room for .webp extension
    if len(original_filename) > max_filename_length:
        # Create a hash of the original URL for uniqueness
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        # Get file extension
        file_ext = os.path.splitext(original_filename)[1] or '.jpg'
        # Create shorter filename with hash
        original_filename = f"img_{url_hash}{file_ext}"

    # Remove any problematic characters from filename
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', original_filename)
    local_path = output_path / safe_filename

    logger.info(f"Downloading image from {image_url}")
    response = requests.get(image_url, stream=True, timeout=10)
    response.raise_for_status()

    # Save the image
    with open(local_path, 'wb') as img_file:
        for chunk in response.iter_content(chunk_size=8192):
            img_file.write(chunk)

    # Convert to WebP
    webp_path = convert_to_webp(local_path)
    if not webp_path:
        raise ValueError(f"Failed to convert {local_path} to WebP")

    logger.info(f"Downloaded and converted image to {webp_path}")
    return webp_path


def delete_remote_images(markdown_file_path, output_file_path=None):
    """Remove all remote image references from a markdown file."""
    # Read the markdown content
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all image references in markdown
    image_pattern = re.compile(
        r'(!\[.*?\]\((.*?)\)|<img.*?src=[\'\"](.*?)[\'\"].*?>)')

    # Process each image reference
    deleted_count = 0
    for match in image_pattern.finditer(content):
        full_match = match.group(1)
        image_url = match.group(2) or match.group(3)

        # Check if it's a remote URL
        if image_url and not image_url.startswith(('/', '.', 'data')) and '://' in image_url:
            content = content.replace(full_match, '')
            deleted_count += 1

    # Write the updated content
    output_file_path = output_file_path or markdown_file_path
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    logger.info(f"Removed {deleted_count} remote image references")

    return output_file_path


def extract_image_urls(markdown_file_path):
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    image_pattern = re.compile(
        r'!\[.*?\]\((.*?)\)|<img.*?src=[\'\"](.*?)[\'\"].*?>')

    image_urls = []
    for match in image_pattern.finditer(content):
        image_url = match.group(1) or match.group(2)
        if image_url and image_url not in image_urls:
            image_urls.append(image_url)

    return image_urls
