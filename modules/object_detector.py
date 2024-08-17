import torch
import cv2


class ObjectDetector:
    def __init__(self, yolov5_model_name="yolov5s"):
        # Load YOLOv5 model for human and animal detection
        self.yolo_model = torch.hub.load("ultralytics/yolov5", yolov5_model_name)
        # Define the classes of interest: human (person) and selected animals
        self.classes_of_interest = [
            "person",
            "dog",
            "cat",
            "horse",
            "sheep",
            "cow",
            "bear",
        ]

    def detect_objects(self, frame):
        # Perform detection using YOLOv5 on the provided frame
        results = self.yolo_model(frame)

        # Extract detected objects of interest
        detected_objects = (
            results.pandas()
            .xyxy[0][["name", "xmin", "ymin", "xmax", "ymax"]]
            .values.tolist()
        )
        filtered_objects = [
            obj for obj in detected_objects if obj[0] in self.classes_of_interest
        ]

        return filtered_objects

    def display_detections(self, roi):
        """
        Detect humans and animals within the ROI and display them on the frame.
        """
        # Detect humans and animals within the ROI
        detected_objects = self.detect_objects(roi)

        # Check for and display detected objects
        for obj in detected_objects:
            name, xmin, ymin, xmax, ymax = obj
            cv2.rectangle(
                roi, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (255, 0, 0), 2
            )
            cv2.putText(
                roi,
                name,
                (int(xmin), int(ymin) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 0, 0),
                2,
            )
            print(f"Detected: {name} in ROI")
