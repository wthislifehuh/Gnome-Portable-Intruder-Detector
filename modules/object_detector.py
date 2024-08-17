import torch
import cv2
from deepface import DeepFace
import os
import re
import logging


class ObjectDetector:
    def __init__(
        self, yolov5_model_name="yolov5s", db_path="./face_recognition/faces/"
    ):
        # Load YOLOv5 model for human and animal detection
        yolo_model_path = "./models/yolov5s.pt"
        self.yolo_model = torch.hub.load(
            "ultralytics/yolov5", "custom", path=yolo_model_path
        )

        # Pre-load DeepFace model for face recognition
        self.face_recognition_model = DeepFace.build_model("Facenet512")

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
        # Face recognition database path
        self.db_path = db_path
        # Initialize the face detector
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

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

    def detect_face(self, person_roi):
        faces = self.face_detector.detectMultiScale(
            person_roi, scaleFactor=1.1, minNeighbors=5
        )
        return faces

    def recognize_face(self, face_img):
        recognition = DeepFace.find(
            img_path=face_img,
            model_name="Facenet512",
            db_path=self.db_path,
            enforce_detection=False,
            silent=True,
        )

        if recognition and not recognition[0].empty:
            filename = (
                recognition[0]["identity"].values[0].split("/")[-1]
            )  # Get the filename, e.g., 'joe_ee2.jpg'
            # Remove the file extension
            name_without_extension = os.path.splitext(filename)[0]  # Get 'joe_ee2'
            # Remove digits from the name
            name_without_numbers = re.sub(
                r"\d+", "", name_without_extension
            )  # Get 'joe_ee'
            # Replace underscores with spaces and capitalize each word
            identity = name_without_numbers.replace("_", " ").title()  # Get 'Joe Ee'
        else:
            identity = "Unknown"

        return identity

    def display_detections(self, roi):
        # Detect humans and animals within the ROI
        detected_objects = self.detect_objects(roi)

        for obj in detected_objects:
            name, xmin, ymin, xmax, ymax = obj

            if name == "person":
                # Crop the area where the person is detected
                person_roi = roi[int(ymin) : int(ymax), int(xmin) : int(xmax)]

                # Detect faces within the person ROI
                faces = self.detect_face(person_roi)

                if len(faces) > 0:
                    for fx, fy, fw, fh in faces:
                        # Crop the face area from the person ROI
                        face_img = person_roi[fy : fy + fh, fx : fx + fw]

                        # Recognize the face
                        # identity = self.recognize_face(face_img)

                        # # Draw a rectangle around the face
                        # cv2.rectangle(
                        #     roi,
                        #     (int(xmin) + fx, int(ymin) + fy),
                        #     (int(xmin) + fx + fw, int(ymin) + fy + fh),
                        #     (0, 255, 0),
                        #     2,
                        # )

                        # # Prepare the text to display
                        # text = f"Name: {identity}"
                        # text_color = (0, 255, 0)  # Green for recognized person

                        # # Calculate text size
                        # (text_width, text_height), _ = cv2.getTextSize(
                        #     text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                        # )

                        # # Ensure text is above the rectangle
                        # y_text = (
                        #     int(ymin) + fy - 10
                        #     if int(ymin) + fy - 10 > text_height
                        #     else int(ymin) + fy + fh + text_height + 10
                        # )

                        # # Overlay the text above the detected face
                        # cv2.putText(
                        #     roi,
                        #     text,
                        #     (int(xmin) + fx, y_text),
                        #     cv2.FONT_HERSHEY_SIMPLEX,
                        #     0.7,
                        #     text_color,
                        #     2,
                        #     cv2.LINE_AA,
                        # )
                else:
                    # If no face is detected, still draw the bounding box for the person
                    cv2.rectangle(
                        roi,
                        (int(xmin), int(ymin)),
                        (int(xmax), int(ymax)),
                        (255, 0, 0),
                        2,
                    )
                    text = "Person"
                    text_color = (255, 0, 0)  # Blue for person without face detected

                    # Overlay the text above the detected person
                    cv2.putText(
                        roi,
                        text,
                        (int(xmin), int(ymin) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        text_color,
                        2,
                        cv2.LINE_AA,
                    )

            else:
                # For other objects (animals), just draw the bounding box and label
                cv2.rectangle(
                    roi, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (255, 0, 0), 2
                )
                cv2.putText(
                    roi,
                    name,
                    (int(xmin), int(ymin) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2,
                )

            print(f"Detected: {name} in ROI")
