import os
import io
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.preprocessing import image
from PIL import Image

app = Flask(__name__)

# Load model
MODEL_PATH = 'batako_batagor_model.h5'
model = None

try:
    # Attempt to load the model. 
    # Note: If custom objects were used during training (like MobileNet), 
    # we might need to pass custom_objects={'MobileNet': ...} or simply load the full model if saved fully.
    # For standard transfer learning save, it usually works out of the box or might warn.
    model = load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

def preprocess_image(img, target_size):
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize(target_size)
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0  # Rescale like MobileNet usually requires (or use preprocess_input)
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    img = Image.open(file.stream)
    
    # Adjust target_size to match your model's input
    processed_img = preprocess_image(img, target_size=(224, 224))
    
    preds = model.predict(processed_img)
    
    # Assuming binary classification: 0 for Batako, 1 for Batagor (or vice versa)
    # You might need to check your class indices from training.
    # Usually: 0 -> Batako, 1 -> Batagor (alphabetical) or similar.
    # We will return the probability and a tentative label.
    
    # Adjust threshold as needed
    score = preds[0][0] # If binary sigmoid
    
    # If using softmax with 2 classes, preds[0] would have 2 values.
    # Let's inspect shape dynamically if needed, but for now assuming binary sigmoid or 2-class softmax.
    
    label = "Unknown"
    confidence = 0.0
    
    if len(preds[0]) == 1:
        # Sigmoid output
        if score < 0.5:
            label = "Batagor" # Replace with actual class 0
            confidence = 1 - score
        else:
            label = "Batako" # Replace with actual class 1
            confidence = score
    else:
        # Softmax output
        class_idx = np.argmax(preds[0])
        confidence = float(preds[0][class_idx])
        # Mapping needs to be known. Assuming alphabetical usually unless specified.
        # Batagor vs Batako
        classes = ['Batagor', 'Batako'] # Alphabetical order default in Keras FlowFromDirectory
        if class_idx < len(classes):
            label = classes[class_idx]
        else:
            label = f"Class {class_idx}"

    return jsonify({'label': label, 'confidence': float(confidence)})

if __name__ == '__main__':
    app.run(debug=True)
