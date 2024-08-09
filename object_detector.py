import torch
from facenet_pytorch import MTCNN
import cv2


class ObjectDetector:
    def __init__(self, yolov5_model_name="yolov5s"):
        # Load YOLOv5 model for animal detection
        self.yolo_model = torch.hub.load("ultralytics/yolov5", yolov5_model_name)
        # Define the animal classes of interest
        self.animal_classes = [
            "dog",
            "cat",
            "horse",
            "sheep",
            "cow",
            "bear",
        ]

        # Load MTCNN model for face detection
        self.mtcnn = MTCNN(keep_all=True)

    def detect_animals(self, frame):
        # Perform detection using YOLOv5 on the provided frame
        results = self.yolo_model(frame)

        # Extract detected animals
        detected_animals = (
            results.pandas()
            .xyxy[0][["name", "xmin", "ymin", "xmax", "ymax"]]
            .values.tolist()
        )
        filtered_animals = [
            obj for obj in detected_animals if obj[0] in self.animal_classes
        ]

        return filtered_animals

    def detect_faces(self, frame):
        # Perform face detection using MTCNN
        boxes, _ = self.mtcnn.detect(frame)

        # Convert the bounding boxes to the format expected by the rest of the pipeline
        detected_faces = []
        if boxes is not None:
            for box in boxes:
                xmin, ymin, xmax, ymax = box
                detected_faces.append(["face", xmin, ymin, xmax, ymax])

        return detected_faces

    def detect_objects(self, frame):
        # Detect animals using YOLOv5
        animals = self.detect_animals(frame)

        # Detect faces using MTCNN
        faces = self.detect_faces(frame)

        # Combine results
        return animals + faces

    def display_detections(self, roi):
        """
        Detect animals and faces within the ROI and display them on the frame.
        """
        # Detect animals and faces within the ROI
        detected_objects = self.object_detector.detect_objects(roi)

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
