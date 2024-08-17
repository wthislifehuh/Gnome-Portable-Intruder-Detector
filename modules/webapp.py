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
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    start_flask_app()
