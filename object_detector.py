import torch
import cv2


class ObjectDetector:
    def __init__(self, model_name="yolov5s"):
        # Load YOLOv5 model
        self.model = torch.hub.load("ultralytics/yolov5", model_name)

    def detect_objects(self, frame):
        # Perform detection on the provided frame
        results = self.model(frame)

        # Extract detected object names and bounding boxes
        detected_objects = (
            results.pandas()
            .xyxy[0][["name", "xmin", "ymin", "xmax", "ymax"]]
            .values.tolist()
        )

        return detected_objects
