import cv2
from flask import Response, stream_with_context
from event_detector import EventDetector


class Camera:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.cap = None
        self.event_detector = EventDetector()

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

    def process_video(self):
        line_position = 200

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

            else:
                print("No Event Detected in ROI")

            cv2.imshow("Camera Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def stream_video(self):
        return Response(
            self.process_video(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
