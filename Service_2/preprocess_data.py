import os
import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import shutil

# Directories
input_dir = 'train'  # Ensure this is the correct path to your training images
output_dir = 'augmented_images'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# ImageDataGenerator for augmentation
datagen = ImageDataGenerator(
    rotation_range=20,  # Only rotation
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest'
)

def extract_label(filename):
    return filename.split('.')[0]  # Adjust label extraction as needed

def augment_image(image_path, save_to_dir, filename):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to load image: {image_path}")
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, 0)
    i = 0
    for batch in datagen.flow(img, batch_size=1, save_to_dir=save_to_dir, save_prefix=f'aug_{i}_{filename.split(".")[0]}', save_format='jpg'):
        i += 1
        if i > 5:  # Generate 5 augmented images per input image
            break
    print(f"Augmented {image_path} to {save_to_dir}")

# Lists to store image paths and labels
train_images = []
train_labels = []

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.JPG') or filename.endswith('.jpeg') or filename.endswith('.jpg'):
        file_path = os.path.join(input_dir, filename)
        augment_image(file_path, output_dir, filename)
        
        # Copy original image to output directory and generate label
        shutil.copyfile(file_path, os.path.join(output_dir, filename))  # Use shutil to copy the file
        train_images.append(os.path.join(output_dir, filename))  # Add the original image to the list
        train_labels.append(extract_label(filename))  # Add the label for the original image
        print(f"Copied {filename} to {output_dir}")
    else:
        print(f"Skipping non-image file: {filename}")

# Save the lists of images and labels
np.save('train_images.npy', train_images)
np.save('train_labels.npy', train_labels)
