from flask import Flask, render_template
from camera import Camera

app = Flask(__name__)

# Initialize the VideoStream object
video_stream = Camera(camera_index=0)


# Route for home page
@app.route("/")
def index():
    return render_template("index.html")


# Route for video feed
@app.route("/video_feed")
def video_feed_route():
    return video_stream.video_feed()


if __name__ == "__main__":
    app.run(debug=True)
