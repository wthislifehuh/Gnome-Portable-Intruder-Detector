from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response, send_from_directory
from camera import Camera
import os
from threading import Thread
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager
from app import validate_signIn, validate_signUp, update_password, upload_photo, store_subscription_code, remove_subscription_code, add_chatID



app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    ),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
)

sub_manager = SubscriptionManager()
app.secret_key = 'your_secret_key'  # Needed for session management

channel = "030326"
# Initialize the Camera object
camera = Camera(channel, camera_index=0)
cap = camera.start_camera()

# Start the video processing in a separate thread
video_processing_thread = Thread(target=camera.process_video, daemon=True)
video_processing_thread.start()


# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")
app.add_url_rule('/validate_signIn', 'validate_signIn', validate_signIn, methods=['POST'])
app.add_url_rule('/validate_signUp', 'validate_signUp', validate_signUp, methods=['POST'])
app.add_url_rule('/update_password', 'update_password', update_password, methods=['POST'])
app.add_url_rule('/upload_photo', 'upload_photo', upload_photo, methods=['POST'])
app.add_url_rule('/store_subscription_code', 'store_subscription_code', store_subscription_code, methods=['POST'])
app.add_url_rule('/remove_subscription_code', 'remove_subscription_code', remove_subscription_code, methods=['POST'])
app.add_url_rule('/add_chatID', 'add_chatID', add_chatID, methods=['POST'])

# Home page (home.html - livestream page)
@app.route('/home')
def home():
    return render_template('home.html')

# Route to stream video
@app.route("/stream_video")
def stream_video():
    return camera.stream_video()

# User Account Page
@app.route('/user_account')
def user_account():
    subscription_code = session.get('subscription_code')
    if not subscription_code:
        return redirect(url_for('index'))

    telegram_chat_ids = sub_manager.get_chat_ids_by_subscription_code(subscription_code)
    registered_photos = get_registered_photos(subscription_code)

    return render_template(
        'userAccount.html',
        subscription_code=subscription_code,
        telegram_chat_ids=telegram_chat_ids,
        registered_photos=registered_photos  # Pass this to the template
    )

def get_registered_photos(subscription_code):
    """ Helper function to get list of registered photos from the file system """
    subscription_dir = os.path.join('face_recognition', 'faces', subscription_code)
    if os.path.exists(subscription_dir):
        print(os.listdir(subscription_dir))
        return os.listdir(subscription_dir)  # Return the list of photo filenames
    print(f"Directory does not exist: {subscription_dir}")
    return []

@app.route('/face_recognition/faces/<subscription_code>/<filename>')
def serve_face_images(subscription_code, filename):
    face_directory = os.path.join('face_recognition', 'faces', subscription_code)
    return send_from_directory(face_directory, filename)



def start_flask_app():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    start_flask_app()
