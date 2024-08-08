import cv2
from flask import Response


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def generate_frames(self):
        camera = cv2.VideoCapture(self.camera_index)  # Use 0 for the default camera

        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()

                # Yield the frame as a byte array
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        camera.release()

    def video_feed(self):
        return Response(
            self.generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
