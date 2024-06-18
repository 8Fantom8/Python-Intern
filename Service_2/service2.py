from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import shutil
import os
import pickle

app = FastAPI()

class EmployeeIDResponse(BaseModel):
    employee_id: str

# Load the OCR model
model = tf.keras.models.load_model('ocr_model.h5')

# Load the label encoder
with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

@app.post("/process_image", response_model=EmployeeIDResponse)
async def process_image(image: UploadFile = File(...)):
    # Save the uploaded image to a local directory
    os.makedirs('images', exist_ok=True)
    img_path = f"images/{image.filename}"
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Preprocess the image
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    # Predict the ID
    prediction = model.predict(img_array)
    predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    
    return EmployeeIDResponse(employee_id=predicted_label)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
