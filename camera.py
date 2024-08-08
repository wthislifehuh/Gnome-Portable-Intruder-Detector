import cv2
from flask import Response


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def start_camera(self):
        camera = cv2.VideoCapture(self.camera_index)
        # Make an object instance for frame analyzer here!!!

        while True:
            success, frame = camera.read()
            if not success:
                break
            else:

                # Do analysis here!!!

                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()

                # Yield the frame as a byte array
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        camera.release()

    def stream_video(self):
        return Response(
            self.start_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
