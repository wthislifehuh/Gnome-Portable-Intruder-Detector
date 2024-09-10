import torch
import cv2
from deepface import DeepFace
import os
import re
from scipy.spatial import distance
from embeddings import FaceEmbeddingDB
import numpy as np
import sqlite3
import json


class ObjectDetector:
    def __init__(
        self,
        yolov5_model_name="yolov5n",
        db_file="face_embeddings.db",
        identity_confirmation_frames=30,
    ):
        self.yolo_model = torch.hub.load("ultralytics/yolov5", "yolov5n")
        self.face_recognition_model = DeepFace.build_model("Facenet512")
        self.classes_of_interest = ["person", "dog", "cat"]
        self.db_file = db_file
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        # Caching recognized faces and their bounding boxes
        self.recognized_faces = {}
        self.trackers = {}  # To store the trackers
        self.tracking_ids = {}  # To store recognized identities
        self.identity_frame_counters = (
            {}
        )  # To store the frame count of consistent identities
        self.identity_confirmation_frames = (
            identity_confirmation_frames  # Number of frames to confirm identity
        )

        # Ensure the database exists by calling FaceEmbeddingDB.create_db()
        if not os.path.exists(self.db_file):
            FaceEmbeddingDB(self.db_file).create_db()

    def detect_objects(self, frame):
        """Perform object detection on the frame using YOLOv5."""
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
        """Detect faces in the person's region of interest (ROI)."""
        faces = self.face_detector.detectMultiScale(
            person_roi, scaleFactor=1.1, minNeighbors=5
        )
        return faces

    def get_embeddings_from_db(self):
        """Fetch all embeddings and their corresponding image filenames from the database."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT embedding_name, embedding FROM face_embeddings")
        rows = cursor.fetchall()
        conn.close()

        embeddings = []
        for row in rows:
            embedding_name = row[0]
            embedding_json = row[1]
            try:
                embedding_data = json.loads(embedding_json)
                embedding = np.array(embedding_data[0]["embedding"])
                embeddings.append((embedding_name, embedding))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing embedding for {embedding_name}: {e}")

        return embeddings

    def recognize_face(self, face_img):
        """Recognize a face using embeddings stored in the local database."""
        face_hash = hash(face_img.tobytes())
        if face_hash in self.recognized_faces:
            return self.recognized_faces[face_hash]

        input_embedding = DeepFace.represent(
            img_path=face_img, model_name="Facenet512", enforce_detection=False
        )
        if not input_embedding:
            return "Unknown"

        input_embedding = np.array(input_embedding[0]["embedding"])
        stored_embeddings = self.get_embeddings_from_db()

        best_match = None
        best_distance = float("inf")

        for embedding_name, stored_embedding in stored_embeddings:
            dist = distance.cosine(input_embedding, stored_embedding)
            if dist < best_distance:
                best_distance = dist
                best_match = embedding_name

        if best_match and best_distance < 0.4:
            filename = os.path.basename(best_match)
            name_without_extension = os.path.splitext(filename)[0]
            name_without_numbers = re.sub(r"\d+", "", name_without_extension)
            identity = name_without_numbers.split("_")[0].title()
        else:
            identity = "Unknown"

        self.recognized_faces[face_hash] = identity
        return identity

    def initialize_tracker(self, obj_name, bbox, frame):
        tracker = cv2.legacy.TrackerKCF_create()  # Initialize tracker
        tracker.init(frame, bbox)
        tracker_id = f"{obj_name}_{bbox[0]}_{bbox[1]}"
        self.trackers[tracker_id] = tracker
        self.tracking_ids[tracker_id] = {"identity": "Unknown", "confirmed": False}
        self.identity_frame_counters[tracker_id] = {"identity": "Unknown", "counter": 0}
        return tracker_id

    def update_trackers(self, frame):
        """Update all existing trackers and check for identity confirmation."""
        ids_to_remove = []
        for tracker_id, tracker in self.trackers.items():
            success, bbox = tracker.update(frame)

            if success:
                x, y, w, h = [int(v) for v in bbox]

                # Ensure that tracking_ids stores a dictionary, not a string
                if isinstance(self.tracking_ids.get(tracker_id), str):
                    # If it's a string (identity), convert it to a dictionary
                    self.tracking_ids[tracker_id] = {
                        "identity": self.tracking_ids[tracker_id],
                        "confirmed": False,
                    }

                # Now access the identity info safely
                current_identity_info = self.tracking_ids.get(
                    tracker_id, {"identity": "Unknown", "confirmed": False}
                )
                current_identity = current_identity_info["identity"]
                confirmed = current_identity_info["confirmed"]

                if confirmed:
                    # If identity is already confirmed, just display it
                    identity = current_identity
                else:
                    # Otherwise, try to recognize the face again
                    person_roi = frame[y : y + h, x : x + w]
                    faces = self.detect_face(person_roi)

                    if len(faces) > 0:
                        for fx, fy, fw, fh in faces:
                            face_img = person_roi[fy : fy + fh, fx : fx + fw]
                            identity = self.recognize_face(face_img)

                            # Check if identity remains the same across frames
                            identity_counter = self.identity_frame_counters.get(
                                tracker_id, {"identity": "Unknown", "counter": 0}
                            )

                            if identity == identity_counter["identity"]:
                                identity_counter["counter"] += 1
                            else:
                                # If identity changes, reset the counter
                                identity_counter["counter"] = 1
                                identity_counter["identity"] = identity

                            # Confirm the identity if it remains the same for enough frames
                            if (
                                identity_counter["counter"]
                                >= self.identity_confirmation_frames
                            ):
                                self.tracking_ids[tracker_id] = {
                                    "identity": identity,
                                    "confirmed": True,
                                }

                            # Update the identity frame counter
                            self.identity_frame_counters[tracker_id] = identity_counter

                # Draw bounding box and confirmed identity label
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Identity: {current_identity}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            else:
                ids_to_remove.append(tracker_id)

        # Remove trackers that have failed
        for tracker_id in ids_to_remove:
            del self.trackers[tracker_id]
            del self.tracking_ids[tracker_id]
            del self.identity_frame_counters[tracker_id]

    def analyze_object(self, frame):
        """Detect and recognize objects in the frame."""
        # Dictionary to return results
        result = {
            "is_intruder": False,
            "intruders": [],
            "is_animal": False,
            "animal": [],
        }

        # Detect objects in the frame
        detected_objects = self.detect_objects(frame)

        for obj in detected_objects:
            name, xmin, ymin, xmax, ymax = obj
            bbox = (int(xmin), int(ymin), int(xmax - xmin), int(ymax - ymin))

            if name == "person":
                # Crop the person's ROI for face detection and recognition
                person_roi = frame[int(ymin) : int(ymax), int(xmin) : int(xmax)]
                faces = self.detect_face(person_roi)

                if len(faces) > 0:
                    for fx, fy, fw, fh in faces:
                        face_img = person_roi[fy : fy + fh, fx : fx + fw]
                        identity = self.recognize_face(face_img)

                        if identity == "Unknown":
                            result["is_intruder"] = True
                            result["intruders"].append("Unknown")

                        # Initialize a new tracker for the person
                        tracker_id = self.initialize_tracker("person", bbox, frame)
                        self.tracking_ids[tracker_id] = identity

                        # Draw the face bounding box and identity label
                        cv2.rectangle(
                            frame,
                            (int(xmin) + fx, int(ymin) + fy),
                            (int(xmin) + fx + fw, int(ymin) + fy + fh),
                            (0, 255, 0),
                            2,
                        )
                        cv2.putText(
                            frame,
                            f"Name: {identity}",
                            (int(xmin) + fx, int(ymin) + fy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                else:
                    result["is_intruder"] = True
                    result["intruders"].append("Unknown")
                    cv2.rectangle(
                        frame,
                        (int(xmin), int(ymin)),
                        (int(xmax), int(ymax)),
                        (255, 0, 0),
                        2,
                    )
                    cv2.putText(
                        frame,
                        "Person",
                        (int(xmin), int(ymin) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 0, 0),
                        2,
                    )

            else:
                # Initialize a tracker for the detected animal
                tracker_id = self.initialize_tracker(name, bbox, frame)
                self.tracking_ids[tracker_id] = name

                # Draw bounding box and label for the animal
                result["is_animal"] = True
                result["animal"].append(name)
                cv2.rectangle(
                    frame,
                    (int(xmin), int(ymin)),
                    (int(xmax), int(ymax)),
                    (255, 0, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    name,
                    (int(xmin), int(ymin) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2,
                )

            print(f"Detected: {name} in frame")
        return result
