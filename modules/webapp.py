# droidcam on mobile device

from flask import Flask, render_template
from camera import Camera
import os

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
