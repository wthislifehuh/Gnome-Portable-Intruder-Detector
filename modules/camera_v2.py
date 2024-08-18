import cv2
from flask import Response, stream_with_context
from event_detector import EventDetector
from object_detector import ObjectDetector
import time


class Camera:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.cap = None
        self.event_detector = EventDetector()
        self.object_detector = ObjectDetector()

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return False
        return self.cap

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()

    def process_video(
        self,
        frame_skip=5,
        notification_cooldown=10,
        intruder_debounce_threshold=3,
        animal_debounce_threshold=3,
    ):
        line_position = 200
        frame_count = 0
        person_last_notification_time = 0
        animal_last_notification_time = 0
        intruder_counter = 0
        animal_counter = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Increment the frame count
            frame_count += 1

            # Skip frames based on the frame_skip parameter
            if frame_count % frame_skip != 0:
                continue

            # ---------------------------------------- Frame analysis starts here ----------------------------------------

            # Draw the vertical line to separate inside and outside areas
            cv2.line(
                frame,
                (line_position, 0),
                (line_position, frame.shape[0]),
                (0, 255, 0),
                2,
            )

            # Define the region of interest (ROI) to the right of the vertical line
            roi = frame[:, line_position:]

            fg_mask, is_event = self.event_detector.analyze_frame(roi)

            if is_event:
                print("Event Detected in ROI")
                result = self.object_detector.analyze_object(roi)
                print(result)

                if result["is_intruder"]:  # If intruder is detected
                    intruder_counter += 1  # Update intruder counter

                    if (
                        intruder_counter >= intruder_debounce_threshold
                    ):  # Confirm that an intruder is detected

                        current_time = time.time()

                        if (
                            current_time - person_last_notification_time
                            > notification_cooldown
                        ):  # Make sure that the notification is sent only after certain threshold
                            # Trigger notification module here!!!
                            print("Trigger intruder notification")
                            person_last_notification_time = current_time

                if result["is_animal"]:  # If animal is detected
                    animal_counter += 1  # Update animal counter

                    if (
                        animal_counter >= animal_debounce_threshold
                    ):  # Confirm that animal is detected

                        current_time = time.time()

                        if (
                            current_time - animal_last_notification_time
                            > notification_cooldown
                        ):  # Make sure that the notification is sent only after certain threshold
                            # Trigger notification module here!!!
                            print(result["animal"])
                            print("Trigger animal notification")
                            animal_last_notification_time = current_time

            else:
                print("No Event Detected in ROI")

            # Display the current frame
            cv2.imshow("Camera Feed", frame)

            # Check for user input to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def generate_frame(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Encode the frame to JPEG format
            ret, buffer = cv2.imencode(".jpg", frame)
            processed_frame = buffer.tobytes()

            # Yield the frame as a byte array
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + processed_frame + b"\r\n"
            )

    def stream_video(self):
        return Response(
            self.generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
