import cv2
from flask import Response, stream_with_context


class Camera:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.cap = None

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return False
        return self.cap

    def stream_video(self):
        @stream_with_context
        def generate():
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Encode the frame to JPEG format
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()

                # Yield the frame as a byte array
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        return Response(
            generate(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    def process_video_frame(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            # Display the frame using OpenCV
            cv2.imshow("Camera Feed", frame)

            # Press 'q' to exit the video feed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


