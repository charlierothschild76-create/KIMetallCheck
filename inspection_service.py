from .defect_detection import DefectDetector
from .measurement import Measurement
from .image_preprocessing import ImagePreprocessor
import cv2
import numpy as np
import os

class InspectionService:
    def __init__(self, model_path="yolov8n.pt", camera_matrix=None, dist_coeffs=None):
        self.defect_detector = DefectDetector(model_path)
        self.image_preprocessor = ImagePreprocessor()
        if camera_matrix is None or dist_coeffs is None:
            # Provide dummy camera parameters if not provided for basic functionality
            print("Warning: Camera parameters not provided. Using dummy values for measurement.")
            camera_matrix = [[1000.0, 0.0, 640.0], [0.0, 1000.0, 480.0], [0.0, 0.0, 1.0]]
            dist_coeffs = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.measurement_module = Measurement(camera_matrix, dist_coeffs)
        print("InspectionService initialized.")

    def perform_inspection(self, image_path, measurement_points=None, real_world_unit_per_pixel=None):
        """
        Performs a complete inspection on an image, including defect detection and measurement.
        Args:
            image_path (str): Path to the image to inspect.
            measurement_points (list, optional): List of pixel coordinates for measurement.
            real_world_unit_per_pixel (float, optional): Scale for simplified measurement.
        Returns:
            dict: A dictionary containing defect detection results and measurement results.
        """
        print(f"Performing inspection on image: {image_path}")

        # 1. Image Preprocessing for robustness
        preprocessed_image_path = "preprocessed_for_inspection.jpg"
        self.image_preprocessor.preprocess_image(image_path, preprocessed_image_path)

        # 2. Defect Detection on preprocessed image
        defects = self.defect_detector.detect_defects(preprocessed_image_path)

        # 3. Measurement (if points are provided) on preprocessed image
        measurements = None
        if measurement_points:
            measurements = self.measurement_module.measure_object_dimensions(
                preprocessed_image_path, measurement_points, real_world_unit_per_pixel
            )

        # 4. Visualize results (optional, for debugging/demonstration)
        output_image_path = "inspection_results.jpg"
        self._visualize_inspection_results(preprocessed_image_path, defects, measurements, output_image_path)

        print("Inspection complete.")
        return {"defects": defects, "measurements": measurements}

    def _visualize_inspection_results(self, image_path, defects, measurements, output_path):
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return

        # Draw defect bounding boxes
        for defect in defects:
            x1, y1, x2, y2 = map(int, defect["box"])
            confidence = defect["confidence"]
            class_name = defect["class"]
            color = (0, 0, 255)  # Red for defects
            thickness = 2
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

        # Draw measurement results (simplified for now)
        if measurements and "measured_length" in measurements:
            text = f'Measured Length: {measurements["measured_length"]:.2f}'
            cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2) # Green for measurements

        cv2.imwrite(output_path, img)
        print(f"Inspection results visualized and saved to: {output_path}")

if __name__ == "__main__":
    # Example Usage:
    # Ensure a dummy image exists for testing
    dummy_image_path = "data/simulated_defects/image_000.jpg"
    if not os.path.exists(dummy_image_path):
        os.makedirs(os.path.dirname(dummy_image_path), exist_ok=True)
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
        cv2.imwrite(dummy_image_path, dummy_img)
        with open(os.path.join(os.path.dirname(dummy_image_path), "image_000.txt"), "w") as f:
            f.write("0 0.5 0.5 0.1 0.1")
        print(f"Created dummy image at {dummy_image_path}")

    # Initialize InspectionService (using dummy camera params for now)
    inspection_service = InspectionService()

    # Perform inspection with both defect detection and a dummy measurement
    dummy_measurement_points = [[100, 100], [200, 100]]
    dummy_real_world_unit_per_pixel = 0.01

    results = inspection_service.perform_inspection(
        dummy_image_path, dummy_measurement_points, dummy_real_world_unit_per_pixel
    )
    print("Full Inspection Results:", results)


