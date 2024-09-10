import cv2
from flask import Response, stream_with_context
from event_detector import EventDetector
from object_detector import ObjectDetector
import time
import os
import asyncio
from notification_alarm_handler import NotificationAlarmHandler
from datetime import datetime
from collections import Counter


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
        self.recent_activities = []
        self.activity_updated = False  # Flag to indicate when new activity is added

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

    def process_video(self, frame_skip=15):
        frame_count = 0
        person_notification_sent = (
            False  # Tracks whether an intruder notification has been sent
        )
        animal_notification_sent = (
            False  # Tracks whether an animal notification has been sent
        )
        intruder_tracked = False  # Track whether an intruder is currently being tracked

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
                print("Event detected")
                # Update existing trackers before running object detection
                self.object_detector.update_trackers(frame)

                # Only analyze objects if no active trackers exist
                if not self.object_detector.trackers:
                    result = self.object_detector.analyze_object(
                        frame
                    )  # Detect new objects
                    print(result)

                    # Handle intruder detection (Unknown Person)
                    if result["is_intruder"]:
                        if (
                            not person_notification_sent
                        ):  # Check if notification has already been sent
                            current_time = time.time()

                            # Trigger intruder notification and start recording
                            print("Trigger intruder notification")
                            # asyncio.run(self.notification_alarm_handler.human_trigger())
                            person_notification_sent = True
                            # Log in website
                            self.log_intruder_activity("human")
                            # Uncomment this section when integrating notification module
                            asyncio.run(self.notification_alarm_handler.human_trigger())

                            if not self.is_recording:
                                self.start_recording(self.cap, self.channel)

                        intruder_tracked = True  # Mark that intruder is being tracked

                    # Handle animal detection
                    if result["is_animal"]:
                        if (
                            not animal_notification_sent
                        ):  # Check if notification has already been sent
                            current_time = time.time()

                            # Trigger animal notification
                            print(f"Animal detected: {result['animal']}")
                            print("Trigger animal notification")
                            # Log in website
                            self.log_intruder_activity(result['animal'])
                            animal_notification_sent = True

                            # Uncomment this section when integrating notification module
                            asyncio.run(self.notification_alarm_handler.animal_trigger(result['animal']))

                    # Continuously write frames to the video file while recording
                    if self.is_recording and self.out:
                        self.out.write(frame)

                else:
                    # Update trackers for intruders and animals, and track if intruder is still present
                    active_person_trackers = any(
                        identity["identity"]
                        == "Unknown"  # Track only if it's an unknown person
                        for identity in self.object_detector.tracking_ids.values()
                    )

                    if not active_person_trackers:
                        # If no intruder is being tracked, stop recording and reset notification flag
                        if self.is_recording:
                            self.stop_recording()
                            print("Stopped recording: Intruder is no longer tracked.")
                        person_notification_sent = (
                            False  # Reset to allow for new intruder notifications
                        )
                        intruder_tracked = (
                            False  # Mark that no intruder is being tracked
                        )

                    else:
                        intruder_tracked = True  # Intruder is still being tracked

                    # Check if all animal trackers are lost and reset notification status for animals
                    active_animal_trackers = any(
                        identity["identity"] == "Animal"
                        for identity in self.object_detector.tracking_ids.values()
                    )

                    if not active_animal_trackers:
                        animal_notification_sent = (
                            False  # Reset for new animal detection
                        )

            else:
                print("No event detected.")
                if self.is_recording:
                    self.stop_recording()
                    print("Stopped recording: No event detected.")
            # Display the current frame
            cv2.imshow("Gnome", frame)

            # Check for user input to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def start_recording(self, cap, channel="030326", frame_skip=15):
        # Define the path where the video will be saved
        output_dir = os.path.join(os.getcwd(), "static", "videos", channel)
        os.makedirs(output_dir, exist_ok=True)
        current_datetime = datetime.now()

        # Format the datetime as yymmddhhmmss
        formatted_datetime = current_datetime.strftime("%y%m%d%H%M%S")
        output_filename = formatted_datetime + ".webm"  # Save as WEBM format
        output_filepath = os.path.join(output_dir, output_filename)

        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*"VP80")  # VP8 codec for WEBM format
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        # Set the frame rate to reflect the actual FPS being processed
        actual_fps = 30.0 / frame_skip
        self.out = cv2.VideoWriter(
            output_filepath, fourcc, actual_fps, (frame_width, frame_height)
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

    # Method to log and format recent activity
    def log_intruder_activity(self, intruder):
        current_datetime = datetime.now()
        intrusion_date = current_datetime.strftime("%d/%m/%y")
        intrusion_time = current_datetime.strftime("%H:%M:%S")

        if isinstance(intruder, list):
            animal_count = Counter(intruder)
            formatted_status = []
            for animal, count in animal_count.items():
                animal_name = animal.capitalize() + ('s' if count > 1 else '')
                formatted_status.append(f"{count} {animal_name}")

            if len(formatted_status) == 2:
                intruder = f"{formatted_status[0]} and {formatted_status[1]}"
            elif len(formatted_status) == 1:
                intruder = f"{formatted_status[0]}"
            else:
                intruder = ', '.join(formatted_status[:-1]) + f", and {formatted_status[-1]}"
        else:
            intruder = intruder.capitalize()

        activity_entry = f"{intrusion_date} {intrusion_time} - {intruder} intruder detected."

        # Append to recent activities list (limit to last 10)
        self.recent_activities.append(activity_entry)
        if len(self.recent_activities) > 10:
            self.recent_activities.pop(0)  # Keep only the last 10 activities
        print("log: ", activity_entry)
        self.activity_updated = True  # Set flag to true when new activity is added

    def stream_recent_activity(self):
        def event_stream():
            last_sent = ""  # Store the last sent activity data
            while True:
                if self.activity_updated:
                    data = ','.join(self.recent_activities)
                    print("Recent activity: ", self.recent_activities)
                    if data != last_sent:  # Only send if there's new data
                        yield f"data: {data}\n\n"
                        last_sent = data  # Update last sent data
                    self.activity_updated = False  # Reset the update flag
                time.sleep(1)  # Sleep for 1 second before checking again
        return Response(event_stream(), content_type='text/event-stream')
