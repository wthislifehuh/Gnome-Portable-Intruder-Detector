# droidcam on mobile device

from flask import Flask, render_template
from camera import Camera
import os
import cv2

app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    ),
)

# Initialize the VideoStream object
camera = Camera(camera_index=0)


# Route for home page
@app.route("/")
def index():
    return render_template("index.html")


# Route to stream video
@app.route("/stream_video")
def stream_video():
    return camera.stream_video()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# import cv2

# # DroidCam typically uses IP cameras, and the URL is in this format
# # Replace 'http://your_droidcam_ip:port/mjpegfeed' with your actual DroidCam IP and port
# droidcam_url = "http://192.168.1.17:4747"

# # Open the video capture with the DroidCam URL
# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # or cv2.CAP_MSMF

# if not cap.isOpened():
#     print("Error: Could not open video stream from DroidCam.")
# else:
#     print("Connected to DroidCam successfully.")

#     while True:
#         # Capture frame-by-frame
#         ret, frame = cap.read()

#         if not ret:
#             print("Error: Could not read frame.")
#             break

#         # Display the resulting frame
#         cv2.imshow('DroidCam Feed', frame)

#         # Press 'q' to exit the video stream
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # When everything done, release the capture
#     cap.release()
#     cv2.destroyAllWindows()
