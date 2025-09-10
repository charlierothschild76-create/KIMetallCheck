import os
import cv2
import numpy as np

def create_simulated_dataset(output_dir="data/simulated_defects", num_images=10):
    """
    Creates a simulated dataset for defect detection.
    In a real scenario, this would involve generating or augmenting images
    with various types of metal surface defects (scratches, cracks, dents, corrosion).
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Simulated dataset directory created at: {output_dir}")
    print(f"Placeholder for {num_images} simulated images and annotations.")

    # In a real implementation, you would:
    # 1. Load base images of metal parts.
    # 2. Programmatically add defects (e.g., drawing lines for scratches, circles for dents).
    # 3. Generate corresponding YOLO-format annotation files (bounding boxes and class labels).
    # 4. Apply data augmentation techniques (rotation, scaling, brightness changes, etc.).

    # For now, create dummy image files (black images) and dummy annotation files
    for i in range(num_images):
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8) # Create a black image
        cv2.imwrite(os.path.join(output_dir, f"image_{i:03d}.jpg"), dummy_img)
        with open(os.path.join(output_dir, f"image_{i:03d}.txt"), "w") as f:
            f.write("0 0.5 0.5 0.1 0.1") # Dummy annotation: class 0, center x, center y, width, height

    print("Simulated dataset creation complete (placeholder).")

if __name__ == "__main__":
    create_simulated_dataset()


