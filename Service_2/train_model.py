import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Load the image paths and labels
train_images = np.load('train_images.npy')
train_labels = np.load('train_labels.npy')

# Encode labels as integers
label_encoder = LabelEncoder()
train_labels_encoded = label_encoder.fit_transform(train_labels)
train_labels_encoded = train_labels_encoded.astype(str)  # Convert labels to strings

train_images, val_images, train_labels, val_labels = train_test_split(
    train_images, train_labels_encoded, test_size=0.2, random_state=42
)

train_df = pd.DataFrame({"filename": train_images, "label": train_labels})
val_df = pd.DataFrame({"filename": val_images, "label": val_labels})

datagen = ImageDataGenerator(rescale=1./255)  

train_gen = datagen.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='label',
    target_size=(150, 150),
    batch_size=32,
    class_mode='categorical',  
)

val_gen = datagen.flow_from_dataframe(
    val_df,
    x_col='filename',
    y_col='label',
    target_size=(150, 150),
    batch_size=32,
    class_mode='categorical', 
)

# Define the model
base_model = tf.keras.applications.MobileNetV2(input_shape=(150, 150, 3), include_top=False, weights='imagenet')
base_model.trainable = True

x = base_model.output
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x)
predictions = tf.keras.layers.Dense(len(label_encoder.classes_), activation='softmax')(x)

model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)

model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(train_gen, validation_data=val_gen, epochs=10)

# Save the model and the label encoder
model.save('ocr_model.h5')
import pickle
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
