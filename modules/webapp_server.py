from flask import Flask, render_template, request, jsonify
from camera import Camera
import os
from threading import Thread
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager
from app import validate_signIn, validate_signUp, update_password, upload_photo



app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    ),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
)

channel = "030326"
# Initialize the Camera object
camera = Camera(channel, camera_index=0)
cap = camera.start_camera()

# Start the video processing in a separate thread
video_processing_thread = Thread(target=camera.process_video, daemon=True)
video_processing_thread.start()


# Route for the home page
@app.route("/")
def index():
    return render_template("index.html")
app.add_url_rule('/validate_signIn', 'validate_signIn', validate_signIn, methods=['POST'])
app.add_url_rule('/validate_signUp', 'validate_signUp', validate_signUp, methods=['POST'])
app.add_url_rule('/update_password', 'update_password', update_password, methods=['POST'])
app.add_url_rule('/upload_photo', 'upload_photo', upload_photo, methods=['POST'])

@app.route('/home')
def home():
    return render_template('home.html')


# Route to stream video
@app.route("/stream_video")
def stream_video():
    return camera.stream_video()


def start_flask_app():
    # Start the Flask web server without debug mode
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    start_flask_app()
