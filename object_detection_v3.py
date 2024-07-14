import torch
import clip
from PIL import Image
import time
from pycocotools.coco import COCO
import os

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

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

    # Load image
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)

    # Perform detection
    start_time = time.time()
    with torch.no_grad():
        text_inputs = torch.cat(
            [
                clip.tokenize(f"a photo of a {coco.loadCats(cat_id)[0]['name']}")
                for cat_id in coco.getCatIds()
            ]
        )
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_inputs)

        logits_per_image, logits_per_text = model(image, text_inputs)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    end_time = time.time()

    detected_objects = [
        coco.loadCats(coco.getCatIds()[i])[0]["name"]
        for i in probs[0].argsort()[-5:][::-1]
    ]
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
