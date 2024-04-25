import zipfile
from io import BytesIO
from PIL import Image
from random import choice
import os

def generate_image_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        dirs = set(os.path.dirname(x) for x in z.namelist() if '/' in x)
        layer_folders = sorted(dirs)

        base_image = None


        for folder in layer_folders:

            images = [f for f in z.namelist() if f.startswith(folder + '/') and f.endswith(('.png', '.jpg'))]
            if images:
                image_path = choice(images)
                with z.open(image_path) as file:
                    current_image = Image.open(BytesIO(file.read())).convert("RGBA")

                    if base_image is None:
                        base_image = current_image
                    else:

                        base_image = Image.alpha_composite(base_image, current_image)

        return base_image
