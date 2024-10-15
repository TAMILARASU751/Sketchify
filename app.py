import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['OUTPUT_FOLDER'] = 'static/outputs/'  # Ensure output is in the static folder
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_sketch(image_path, conversion_type, pencil_thickness, edge_sensitivity, brightness, contrast):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not read the image. Please check the file format and path.")

    # Apply selected conversion type
    if conversion_type == 'fine_sketch':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blur = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)

    elif conversion_type == 'soft_sketch':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        sketch = cv2.addWeighted(gray, 0.5, blurred, 0.5, 0)

    elif conversion_type == 'shaded_pencil_art':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1=30, threshold2=edge_sensitivity * 25)
        sketch = cv2.bitwise_and(gray, gray, mask=edges)

    elif conversion_type == 'anime_art':
        # Apply bilateral filter to smooth the image
        smoothed = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
        edges = cv2.Canny(smoothed, 100, 200)  # Edge detection
        sketch = cv2.bitwise_and(smoothed, smoothed, mask=edges)

    elif conversion_type == 'color_pencil_sketch':
        # Use OpenCV's built-in pencilSketch function
        gray, sketch = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)

    # Adjust brightness and contrast
    sketch = cv2.convertScaleAbs(sketch, alpha=contrast, beta=brightness * 100 - 100)

    return sketch

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        print(f"Image uploaded to: {image_path}")  # Debugging line

        # Retrieve form data
        conversion_type = request.form.get('conversion')
        pencil_thickness = int(request.form.get('pencil_thickness', 5))
        edge_sensitivity = int(request.form.get('edge_sensitivity', 5))
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))

        try:
            # Convert image to sketch
            sketch = convert_to_sketch(image_path, conversion_type, pencil_thickness, edge_sensitivity, brightness, contrast)
            output_filename = f'sketch_{filename}'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # Save output image
            cv2.imwrite(output_path, sketch)
            print(f"Saved sketch to: {output_path}")  # Debugging line

            # Return the path to the output image
            output_image_url = url_for('static', filename=f'outputs/{output_filename}')
            print(f"Output image URL: {output_image_url}")  # Debugging line
            return jsonify({'output_image': output_image_url})

        except Exception as e:
            print(f"Error during image conversion: {e}")  # Log the error message
            return jsonify({'error': str(e)}), 500  # Return the error message to the client

    return jsonify({'error': 'File not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
