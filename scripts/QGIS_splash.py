import os
import re
import requests
from PIL import Image  # Added to handle image resizing
from imageio import get_writer, imread
from distutils.version import LooseVersion

# Constants
GITHUB_URL = 'https://github.com/qgis/QGIS'
REPO_API_URL = 'https://api.github.com/repos/qgis/QGIS/tags'
OUTPUT_DIR = 'splash_images'
GIF_FILENAME = 'qgis_splash.gif'
GIF_DELAY = 500  # seconds
PER_PAGE = 100  # Number of tags to fetch per page
RESIZE_DIMENSIONS = (1977, 946)  # Target dimensions for resizing

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Helper function to convert tag name from final-X_Y_Z format to X.Y
def convert_version(tag_name):
    match = re.match(r'final-(\d+)_(\d+)_\d+', tag_name)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return None

# Helper function to handle GitHub API pagination
def get_paginated_tags(url):
    tags = []
    while url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                tags.extend(response.json())
                
                # Check if there are more pages by looking at the 'Link' header
                if 'Link' in response.headers:
                    links = response.headers['Link']
                    # Extract the URL for 'rel="next"' and clean it up
                    next_link = [l.split(';')[0].strip('<> ') for l in links.split(',') if 'rel="next"' in l]
                    url = next_link[0] if next_link else None  # Continue to the next page
                else:
                    break
            else:
                print(f"Failed to fetch tags: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    return tags

# Get a list of tags from the GitHub repository with pagination
def get_final_tags():
    url = f"{REPO_API_URL}?per_page={PER_PAGE}"
    tags = get_paginated_tags(url)
    
    if tags:
        versions = set()  # To avoid duplicates
        final_tags = []

        for tag in tags:
            tag_name = tag['name']
            if 'final' in tag_name:  # Filter for tags containing 'final'
                version = convert_version(tag_name)
                if version and version not in versions:
                    versions.add(version)
                    final_tags.append({'name': tag_name, 'version': version})

        return final_tags
    else:
        print("No tags found.")
        return []

# Download the splash.png for a given tag
def download_splash_image(tag, version):
    splash_url = f"{GITHUB_URL}/raw/{tag}/images/splash/splash.png"
    try:
        splash_response = requests.get(splash_url)
        if splash_response.status_code == 200:
            splash_filename = os.path.join(OUTPUT_DIR, f"splash_{version}.png")
            with open(splash_filename, 'wb') as file:
                file.write(splash_response.content)
            print(f"Downloaded splash image for {tag} ({version})")
            return splash_filename
        else:
            print(f"Failed to download splash for {tag}: {splash_response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Resize the image to the specified dimensions
def resize_image(image_path):
    try:
        with Image.open(image_path) as img:
            resized_img = img.resize(RESIZE_DIMENSIONS, Image.ANTIALIAS)
            resized_img.save(image_path)  # Save the resized image over the original
            print(f"Resized image: {image_path}")
    except Exception as e:
        print(f"Failed to resize image {image_path}: {e}")

# Create a GIF from the downloaded splash images
def create_gif(images):
    with get_writer(GIF_FILENAME, mode='I', duration=GIF_DELAY) as writer:
        for image in images:
            img = imread(image)
            writer.append_data(img)
    print(f"GIF created: {GIF_FILENAME}")

def main():
    tags = get_final_tags()
    if not tags:
        print("No final tags found, aborting.")
        return

    # List all found tags with their versions
    print("Found tags:")
    for tag_info in tags:
        print(f"Tag: {tag_info['name']}, Version: {tag_info['version']}")
    
    # Sort tags by version
    tags.sort(key=lambda x: LooseVersion(x['version']))

    # Download splash images and collect file paths
    downloaded_images = []
    for tag_info in tags:
        tag = tag_info['name']
        version = tag_info['version']
        splash_image = download_splash_image(tag, version)
        if splash_image:
            resize_image(splash_image)  # Resize image after downloading
            downloaded_images.append(splash_image)
    
    if downloaded_images:
        create_gif(downloaded_images)
    else:
        print("No images downloaded, GIF creation skipped.")

if __name__ == "__main__":
    main()
