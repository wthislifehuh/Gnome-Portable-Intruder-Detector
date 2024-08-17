import cv2
from flask import Response
from event_detector import EventDetector
from object_detector import ObjectDetector


class Camera:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.event_detector = EventDetector()
        self.object_detector = ObjectDetector()  # Initialize the ObjectDetector

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
                print("Event Detected in ROI")

                # Invoke object detection module here!!!

                self.object_detector.display_detections(roi)

            else:
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
        cv2.destroyAllWindows()

    def stream_video(self):
        return Response(
            self.start_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
