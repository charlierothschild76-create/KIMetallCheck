#!/usr/bin/env python3
"""
Integration test script for the Metal Inspection App
Tests the complete workflow from image upload to results
"""

import requests
import json
import time
import os
import base64
from PIL import Image
import numpy as np

def test_api_health():
    """Test if the API is running and healthy"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ API Health Check: PASSED")
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API Health Check: FAILED (Error: {e})")
        return False

def create_test_image():
    """Create a simple test image for inspection"""
    # Create a simple test image (640x640 with some patterns)
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Add some patterns to simulate a metal part
    img[100:200, 100:500] = [128, 128, 128]  # Gray rectangle
    img[300:400, 200:400] = [64, 64, 64]     # Darker rectangle (simulated defect area)
    
    # Save as temporary file
    test_image_path = "test_metal_part.jpg"
    Image.fromarray(img).save(test_image_path)
    return test_image_path

def test_image_inspection_multipart():
    """Test image inspection using multipart form data"""
    try:
        test_image_path = create_test_image()
        
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'measurement_points': json.dumps([[100, 100], [500, 100]]),
                'scale_factor': '0.01'
            }
            
            response = requests.post(
                "http://localhost:5000/api/inspect",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Image Inspection (Multipart): PASSED")
            print(f"  Success: {result.get('success')}")
            if 'results' in result:
                defects = result['results'].get('defects', [])
                measurements = result['results'].get('measurements')
                print(f"  Defects found: {len(defects)}")
                if measurements:
                    print(f"  Measurements: {measurements}")
            return True
        else:
            print(f"✗ Image Inspection (Multipart): FAILED (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Image Inspection (Multipart): FAILED (Error: {e})")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_image_inspection_base64():
    """Test image inspection using base64 encoded image"""
    try:
        test_image_path = create_test_image()
        
        # Convert image to base64
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            'image_data': image_data,
            'measurement_points': [[100, 100], [500, 100]],
            'scale_factor': 0.01
        }
        
        response = requests.post(
            "http://localhost:5000/api/inspect/base64",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Image Inspection (Base64): PASSED")
            print(f"  Success: {result.get('success')}")
            if 'results' in result:
                defects = result['results'].get('defects', [])
                measurements = result['results'].get('measurements')
                print(f"  Defects found: {len(defects)}")
                if measurements:
                    print(f"  Measurements: {measurements}")
            return True
        else:
            print(f"✗ Image Inspection (Base64): FAILED (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Image Inspection (Base64): FAILED (Error: {e})")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_settings_api():
    """Test settings API endpoints"""
    try:
        # Test GET settings
        response = requests.get("http://localhost:5000/api/settings", timeout=5)
        if response.status_code == 200:
            settings = response.json()
            print("✓ Settings GET: PASSED")
            print(f"  Current settings: {settings}")
        else:
            print(f"✗ Settings GET: FAILED (Status: {response.status_code})")
            return False
        
        # Test POST settings
        new_settings = {
            "detection_threshold": 0.9,
            "measurement_tolerance": 0.15,
            "preprocessing_enabled": False
        }
        
        response = requests.post(
            "http://localhost:5000/api/settings",
            json=new_settings,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Settings POST: PASSED")
            print(f"  Update result: {result.get('message')}")
            return True
        else:
            print(f"✗ Settings POST: FAILED (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Settings API: FAILED (Error: {e})")
        return False

def test_frontend_accessibility():
    """Test if the frontend is accessible"""
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend Accessibility: PASSED")
            print(f"  Frontend is accessible at http://localhost:5173/")
            return True
        else:
            print(f"✗ Frontend Accessibility: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend Accessibility: FAILED (Error: {e})")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("METAL INSPECTION APP - INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("Image Inspection (Multipart)", test_image_inspection_multipart),
        ("Image Inspection (Base64)", test_image_inspection_base64),
        ("Settings API", test_settings_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"INTEGRATION TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)

