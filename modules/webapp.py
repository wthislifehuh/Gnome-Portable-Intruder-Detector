from flask import Flask, render_template
from camera_v2 import Camera
import os
from threading import Thread

app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    ),
)

# Initialize the Camera object
camera = Camera(camera_index=0)
cap = camera.start_camera()


# Route for the home page
@app.route("/")
def index():
    return render_template("index.html")


# Route to stream video
@app.route("/stream_video")
def stream_video():
    return camera.stream_video()


def start_flask_app():
    # Start the Flask web server without debug mode
    app.run(host="0.0.0.0", port=5000, debug=False)


def process_camera_frames():
    # Process and display frames using OpenCV
    camera.process_video_frame()


if __name__ == "__main__":
    # Start the Flask app in a separate thread
    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()

    # Start processing frames (this will run in the main thread)
    process_camera_frames()
