import torch
import cv2


class ObjectDetector:
    def __init__(self, model_name="yolov5s"):
        # Load YOLOv5 model
        self.model = torch.hub.load("ultralytics/yolov5", model_name)
        # Define the classes of interest
        self.classes_of_interest = [
            "person",
            "dog",
            "cat",
            "bird",
            "horse",
            "sheep",
            "cow",
            "elephant",
            "bear",
            "zebra",
            "giraffe",
        ]

    def detect_objects(self, frame):
        # Perform detection on the provided frame
        results = self.model(frame)

        # Extract detected objects filtered by classes of interest
        detected_objects = (
            results.pandas()
            .xyxy[0][["name", "xmin", "ymin", "xmax", "ymax"]]
            .values.tolist()
        )
        filtered_objects = [
            obj for obj in detected_objects if obj[0] in self.classes_of_interest
        ]

        return filtered_objects
