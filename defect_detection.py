from ultralytics import YOLO
import os
import cv2
import numpy as np

class DefectDetector:
    def __init__(self, model_path="yolov8n.pt"): # Placeholder for a trained model
        """
        Initializes the DefectDetector with a YOLOv8 model.
        """
        self.model = YOLO(model_path)
        print(f"DefectDetector initialized with model: {model_path}")

    def detect_defects(self, image_path):
        """
        Detects defects in an image using the loaded YOLOv8 model.
        Args:
            image_path (str): Path to the input image.
        Returns:
            list: A list of dictionaries, each representing a detected defect.
                  Each dictionary contains 'box' (bounding box coordinates),
                  'confidence' (detection confidence), and 'class' (defect type).
        """
        print(f"Detecting defects in image: {image_path}")
        results = self.model(image_path)

        detected_defects = []
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()  # Bounding box coordinates (x1, y1, x2, y2)
            confidences = r.boxes.conf.cpu().numpy()  # Confidence scores
            classes = r.boxes.cls.cpu().numpy()  # Class IDs

            for box, conf, cls in zip(boxes, confidences, classes):
                detected_defects.append({
                    "box": box.tolist(),
                    "confidence": float(conf),
                    "class": self.model.names[int(cls)]  # Get class name from model
                })
        print(f"Detected {len(detected_defects)} defects.")
        return detected_defects

    def visualize_defects(self, image_path, defects, output_path="output_defects.jpg"):
        """
        Visualizes detected defects on the image and saves it.
        """
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return

        for defect in defects:
            x1, y1, x2, y2 = map(int, defect["box"])
            confidence = defect["confidence"]
            class_name = defect["class"]

            color = (0, 0, 255)  # Red color for bounding box
            thickness = 2
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

        cv2.imwrite(output_path, img)
        print(f"Visualized defects saved to: {output_path}")

if __name__ == "__main__":
    # Create a dummy image for testing
    dummy_image_path = "data/simulated_defects/image_000.jpg"
    if not os.path.exists(dummy_image_path):
        # Ensure the directory exists and create a dummy image if not already created by dataset_preparation.py
        os.makedirs(os.path.dirname(dummy_image_path), exist_ok=True)
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8) # Black image
        cv2.imwrite(dummy_image_path, dummy_img)
        print(f"Created dummy image at {dummy_image_path}")

    detector = DefectDetector()
    detected_defects = detector.detect_defects(dummy_image_path)
    detector.visualize_defects(dummy_image_path, detected_defects)


