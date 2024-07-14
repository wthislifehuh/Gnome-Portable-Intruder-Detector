import os
from google.cloud import vision
import time
from pycocotools.coco import COCO
import cv2

# Set the environment variable for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "C:/Users/kenho/Desktop/UCCC2513-Mini-Project/cohesive-totem-429413-e3-652ae2430f2e.json"
)

# Set up Google Cloud Vision client
client = vision.ImageAnnotatorClient()

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

# Create a dictionary to map category names to category IDs for COCO dataset
coco_categories = coco.loadCats(coco.getCatIds())
category_name_to_id = {category["name"]: category["id"] for category in coco_categories}

for img_path in image_paths:
    # Get the image ID from the filename
    img_id = int(os.path.splitext(os.path.basename(img_path))[0])

    # Load image
    with open(img_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Perform detection
    start_time = time.time()
    response = client.object_localization(image=image)
    end_time = time.time()

    detected_objects = [
        obj.name.lower() for obj in response.localized_object_annotations
    ]
    print(f"Detected objects in {os.path.basename(img_path)}: {detected_objects}")

    # Get ground truth annotations
    ann_ids = coco.getAnnIds(imgIds=img_id)
    anns = coco.loadAnns(ann_ids)
    ground_truth_objects = [
        coco.loadCats(ann["category_id"])[0]["name"].lower() for ann in anns
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
