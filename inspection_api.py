from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

# Add the parent directory to the path to import our services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.inspection_service import InspectionService
except ImportError:
    # Fallback for direct execution
    sys.path.append('/home/ubuntu/metal_inspection_app/app')
    from services.inspection_service import InspectionService





app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
CORS(app)  # Enable CORS for all routes

# Initialize the inspection service
inspection_service = InspectionService()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Inspection API is running"})

@app.route('/api/inspect', methods=['POST'])
def inspect_image():
    """
    Endpoint to perform inspection on an uploaded image
    Expects: multipart/form-data with 'image' file
    Returns: JSON with defects and measurements
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        # Save the uploaded file temporarily
        temp_image_path = "temp_uploaded_image.jpg"
        file.save(temp_image_path)
        
        # Optional measurement points (if provided)
        measurement_points = None
        if 'measurement_points' in request.form:
            try:
                measurement_points = json.loads(request.form['measurement_points'])
            except json.JSONDecodeError:
                pass
        
        # Optional scale factor
        real_world_unit_per_pixel = None
        if 'scale_factor' in request.form:
            try:
                real_world_unit_per_pixel = float(request.form['scale_factor'])
            except ValueError:
                pass
        
        # Perform inspection
        results = inspection_service.perform_inspection(
            temp_image_path, 
            measurement_points, 
            real_world_unit_per_pixel
        )
        
        # Clean up temporary file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        results = convert_numpy_types(results)
        
        return jsonify({
            "success": True,
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inspect/base64', methods=['POST'])
def inspect_base64_image():
    """
    Endpoint to perform inspection on a base64-encoded image
    Expects: JSON with 'image_data' (base64 string)
    Returns: JSON with defects and measurements
    """
    try:
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 image
        image_data = data['image_data']
        if image_data.startswith('data:image'):
            # Remove data URL prefix if present
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to OpenCV format and save temporarily
        temp_image_path = "temp_base64_image.jpg"
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(temp_image_path, image_cv)
        
        # Optional measurement points
        measurement_points = data.get('measurement_points')
        real_world_unit_per_pixel = data.get('scale_factor')
        
        # Perform inspection
        results = inspection_service.perform_inspection(
            temp_image_path, 
            measurement_points, 
            real_world_unit_per_pixel
        )
        
        # Clean up temporary file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        results = convert_numpy_types(results)
        
        return jsonify({
            "success": True,
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calibrate', methods=['POST'])
def calibrate_camera():
    """
    Endpoint for camera calibration
    Expects: multipart/form-data with multiple 'images' files
    Returns: JSON with calibration parameters
    """
    try:
        files = request.files.getlist('images')
        if not files:
            return jsonify({"error": "No calibration images provided"}), 400
        
        # Save uploaded files temporarily
        temp_paths = []
        for i, file in enumerate(files):
            temp_path = f"temp_calibration_{i}.jpg"
            file.save(temp_path)
            temp_paths.append(temp_path)
        
        # Perform calibration (placeholder)
        from services.camera_calibration import CameraCalibrator
        calibrator = CameraCalibrator()
        calibration_results = calibrator.calibrate_camera(temp_paths)
        
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return jsonify({
            "success": True,
            "calibration": calibration_results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """
    Endpoint to get or update inspection settings
    """
    if request.method == 'GET':
        # Return current settings (placeholder)
        return jsonify({
            "detection_threshold": 0.85,
            "measurement_tolerance": 0.2,
            "preprocessing_enabled": True
        })
    
    elif request.method == 'POST':
        # Update settings (placeholder)
        data = request.get_json()
        # In a real implementation, you would save these settings
        return jsonify({
            "success": True,
            "message": "Settings updated successfully",
            "settings": data
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



@app.route("/demo")
def demo():
    from flask import render_template
    return render_template("realtime_demo.html")


