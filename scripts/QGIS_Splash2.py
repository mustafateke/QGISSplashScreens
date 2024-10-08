import requests
from bs4 import BeautifulSoup
from PIL import Image
import imageio
import os

# Function to get branches starting with "release-"
def get_release_branches():
    branches = []
    page_number = 1
    
    while True:
        url = f"https://github.com/qgis/QGIS/branches/all?page={page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all branch names
        branch_elements = soup.find_all('a', class_='branch-name')
        if not branch_elements:
            break  # Exit if no more branches are found
        
        for branch in branch_elements:
            branch_name = branch.text.strip()
            if branch_name.startswith("release-"):
                branches.append(branch_name)
        
        page_number += 1  # Go to the next page
    
    return branches

# Function to download splash.png from each branch
def download_splash_images(branches):
    splash_images = []
    
    for branch in branches:
        # Construct the URL for the splash.png file in the specific branch
        splash_url = f"https://raw.githubusercontent.com/qgis/QGIS/{branch}/images/splash/splash.png"
        try:
            response = requests.get(splash_url, timeout=10)
            if response.status_code == 200:
                # Save the image with version name
                img_name = f"{branch}.png"
                with open(img_name, 'wb') as img_file:
                    img_file.write(response.content)
                splash_images.append(img_name)
                print(f"Downloaded: {img_name}")
            else:
                print(f"Failed to download {splash_url}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {splash_url}: {e}")
    
    return splash_images

# Function to create a GIF from the downloaded images
def create_gif(image_files, gif_name="splash.gif", duration=1):
    images = []
    for img_file in image_files:
        images.append(imageio.imread(img_file))
    
    imageio.mimsave(gif_name, images, duration=duration)
    print(f"GIF created: {gif_name}")

# Main workflow
if __name__ == "__main__":
    branches = get_release_branches()
    print(f"Found branches: {branches}")

    splash_images = download_splash_images(branches)
    
    if splash_images:
        create_gif(splash_images)
    
    # Cleanup downloaded images
    for img_file in splash_images:
        if os.path.exists(img_file):
            os.remove(img_file)
