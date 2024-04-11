import os
from PIL import Image
from random import choice

def generate_single_image(layers_folder):
    layer_folders = [os.path.join(layers_folder, folder) for folder in os.listdir(layers_folder) if os.path.isdir(os.path.join(layers_folder, folder))]
    layer_folders.sort()

    base_image = None

    for folder in layer_folders:
        images = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.png', '.jpg'))]
        image_path = choice(images)
        current_image = Image.open(image_path).convert("RGBA")

        if base_image is None:
            base_image = current_image
        else:
            base_image = Image.alpha_composite(base_image, current_image)

    return base_image

def generate_multiple_images(layers_folder, output_folder, num_images):
    for i in range(num_images):
        final_image = generate_single_image(layers_folder)
        filename = f'final_image_{i+1}.png'
        final_image.save(os.path.join(output_folder, filename))
        print(f'Generated {filename}')


layers_folder = 'layers/'
output_folder = 'images'
num_images = 100

generate_multiple_images(layers_folder, output_folder, num_images)