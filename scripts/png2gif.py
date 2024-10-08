import imageio
import os
from PIL import Image

import imageio
import os

def create_gif_from_folder(folder_path, output_gif):
    # List all image files in the folder
    images = [img for img in os.listdir(folder_path) if img.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    images.sort()  # Sort the images if needed

    # Create a list to hold image data
    frames = []

    # Read each image and append to frames
    for image in images:
        image_path = os.path.join(folder_path, image)
        frames.append(imageio.imread(image_path))

    # Save the frames as a GIF
    imageio.mimsave(output_gif, frames, duration=500)  # duration in seconds

# Usage


# Example usage
folder_path = 'D:\\Dev\\HLines\\images'  # Replace with your folder path
output_gif_path = 'D:\\Dev\\HLines\\qgis.gif'        # Replace with desired output
create_gif_from_folder(folder_path, output_gif_path)