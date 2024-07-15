import torch
import time
from pycocotools.coco import COCO
import cv2
import os

# Load YOLOv5 model
model = torch.hub.load("ultralytics/yolov5", "yolov5s")

# Paths to the test images and annotations
image_folder = "test_images"
annotation_file = "coco/annotations/instances_val2017.json"

# Initialize COCO ground truth API
coco = COCO(annotation_file)

# Get image filenames in the test_images folder
image_filenames = os.listdir(image_folder)
image_paths = [
    os.path.join(image_folder, filename)
    for filename in image_filenames
    if filename.endswith(".jpg")
]

correct_detections = 0
total_detections = 0
total_images = len(image_paths)
processing_times = []

for img_path in image_paths:
    # Get the image ID from the filename
    img_id = int(os.path.splitext(os.path.basename(img_path))[0])

    # Load image using OpenCV
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to load image {img_path}")
        continue

    # Convert image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Perform detection
    start_time = time.time()
    results = model(img)
    end_time = time.time()

    # Print detected object names
    detected_objects = results.pandas().xyxy[0]["name"].tolist()
    print(f"Detected objects in {os.path.basename(img_path)}: {detected_objects}")

    # Get ground truth annotations
    ann_ids = coco.getAnnIds(imgIds=img_id)
    anns = coco.loadAnns(ann_ids)
    ground_truth_objects = [
        coco.loadCats(ann["category_id"])[0]["name"] for ann in anns
    ]

    # Check correctness of detections
    for det in detected_objects:
        if det in ground_truth_objects:
            correct_detections += 1
        total_detections += 1

    # Record processing time
    processing_times.append(end_time - start_time)

# Calculate accuracy
accuracy = correct_detections / total_detections if total_detections > 0 else 0

# Calculate average processing time per image
avg_processing_time = sum(processing_times) / total_images if total_images > 0 else 0

print(f"Accuracy: {accuracy:.2f}")
print(f"Average processing time per image: {avg_processing_time:.4f} seconds")
