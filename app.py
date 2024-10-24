from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import pandas as pd
import numpy as np
import os
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
import gdown

app = Flask(__name__)

# Load the model
path_to_model = './model.keras'

if not os.path.exists(model_path):
    print("Downloading model...")
    gdown.download('https://drive.google.com/uc?id=1SznbFPkYCgYwmDV-ffdWEcLwAcbG_cmw', model_path, quiet=False)

model = tf.keras.models.load_model(path_to_model)

# Load ingredients CSV
ingredients_df = pd.read_csv('ingr.csv')

# Prediction categories
category = {
    0: 'Burger', 1: 'Chai', 2: 'Chapati', 3: 'Chole Bhature', 4: 'Fried Rice',
    5: 'Idli', 6: 'Jalebi', 7: 'Masala Dosa', 8: 'Momos', 9: 'Pakode', 
    10: 'Pav Bhaji', 11: 'Samosa'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    imagefile = request.files['imagefile']
    allergic_food = request.form['allergic_food']
    
    # Save the uploaded image
    image_path = os.path.join('./images/', secure_filename(imagefile.filename))
    imagefile.save(image_path)
    
    # Preprocess the image for prediction
    img_ = image.load_img(image_path, target_size=(128, 128))
    img_array = image.img_to_array(img_)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.0

    # Predict the food category
    prediction = model.predict(img_processed)
    index = np.argmax(prediction)
    pred_val = category[index]

    # Fetch ingredients of predicted food
    ingredients_list = ingredients_df[pred_val].dropna().tolist()

    # Check if the allergic ingredient is present
    if allergic_food in ingredients_list:
        message = f"The predicted food {pred_val} has {allergic_food}, Don't have it."
    else:
        message = f"No allergic ingredients found in {pred_val}."

    return jsonify({'prediction': pred_val, 'message': message, 'image_path': image_path})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
