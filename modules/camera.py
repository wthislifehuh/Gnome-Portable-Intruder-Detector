import cv2
import os
from flask import Response
from event_detector import EventDetector
from object_detector import ObjectDetector


class Camera:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.event_detector = EventDetector()
        self.object_detector = ObjectDetector()  # Initialize the ObjectDetector
        self.is_recording = False
        self.out = None

    def start_camera(self):
        camera = cv2.VideoCapture(self.camera_index)
        line_position = 200  # Vertical line position (x-coordinate)

        while True:
            success, frame = camera.read()
            if not success:
                break

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

            # Analyze the frame for events within the ROI
            fg_mask, is_event = self.event_detector.analyze_frame(roi)

            if is_event:
                # TODO: NEED to apply this 2 lines of code to if intruders is detected
                if not self.is_recording:
                    self.start_recording(camera)

                print("Event Detected in ROI")

                # Invoke object detection module here
                self.object_detector.display_detections(roi)
            else:
                # TODO: NEED to apply this 2 lines of code to if intruders is NOT detected
                if self.is_recording:
                    self.stop_recording()

                print("No Event Detected in ROI")

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Yield the frame as a byte array
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            # Break loop on 'q' key press (optional for debugging purposes)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()

    def start_recording(self, cap, output_filename="output.mp4"):
        # Define the path where the video will be saved
        output_dir = os.path.join(os.getcwd(), 'assets', 'videos')
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, output_filename)
        
        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        self.out = cv2.VideoWriter(output_filepath, fourcc, 20.0, (frame_width, frame_height))
        self.is_recording = True
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            # Write the frame to the file
            self.out.write(frame)
        print("Recording started...")

    def stop_recording(self):
        self.is_recording = False
        if self.out:
            self.out.release()
            self.out = None
        print("Recording stopped.")

    def stream_video(self):
        return Response(
            self.start_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
