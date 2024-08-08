from flask import Flask, render_template
from camera import Camera

app = Flask(__name__)

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
    app.run(debug=True)
