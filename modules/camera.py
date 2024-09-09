import cv2
from flask import Response, stream_with_context
from event_detector import EventDetector
from object_detector import ObjectDetector
import time
import os
import asyncio
from notification_alarm_handler import NotificationAlarmHandler
from datetime import datetime


class Camera:
    def __init__(self, channel, camera_index):
        self.channel = channel
        self.camera_index = camera_index
        self.cap = None
        self.event_detector = EventDetector()
        self.object_detector = ObjectDetector()
        self.notification_alarm_handler = NotificationAlarmHandler()
        self.is_recording = False
        self.out = None

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
        frame_skip=15,
        notification_cooldown=10,
        intruder_debounce_threshold=30,
        animal_debounce_threshold=30,
    ):
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

            fg_mask, is_event = self.event_detector.analyze_frame(frame)

            if is_event:
                print("Event Detected in frame")
                result = self.object_detector.analyze_object(frame)
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
                            asyncio.run(self.notification_alarm_handler.human_trigger())

                            # Trigger video recording
                            if not self.is_recording:
                                self.start_recording(self.cap, self.channel)
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
                            asyncio.run(
                                self.notification_alarm_handler.animal_trigger(result)
                            )
                            print(result["animal"])
                            print("Trigger animal notification")
                            animal_last_notification_time = current_time

                # Continuously write frames to the video file while recording
                if self.is_recording and self.out:
                    self.out.write(frame)

            else:
                intruder_counter = 0
                animal_counter = 0
                if self.is_recording:
                    self.stop_recording()
                print("No Event Detected in frame")

            # Display the current frame
            cv2.imshow("Camera Feed", frame)

            # Check for user input to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def start_recording(self, cap, channel="030326"):
        # Define the path where the video will be saved
        output_dir = os.path.join(os.getcwd(), "static", "videos", channel)
        os.makedirs(output_dir, exist_ok=True)
        current_datetime = datetime.now()

        # Format the datetime as yymmddhhmmss
        formatted_datetime = current_datetime.strftime('%y%m%d%H%M%S')
        output_filename = formatted_datetime + ".webm"  # Save as WEBM format
        output_filepath = os.path.join(output_dir, output_filename)

        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*"VP80")  # VP8 codec for WEBM format
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        self.out = cv2.VideoWriter(
            output_filepath, fourcc, 20.0, (frame_width, frame_height)
        )
        self.is_recording = True
        print("Recording started...")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.out:
                self.out.release()
                self.out = None
            print("Recording stopped.")
            
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
