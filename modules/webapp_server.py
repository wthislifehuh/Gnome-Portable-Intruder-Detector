from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    Response,
    send_from_directory,
)
from camera import Camera
import os
from threading import Thread
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager
from embeddings import FaceEmbeddingDB
from app import (
    validate_signIn,
    validate_signUp,
    update_password,
    upload_photo,
    process_embeddings,
    store_subscription_code,
    remove_subscription_code,
    add_chatID,  
    delete_chatID,
    update_phoneNum,
)
from datetime import datetime
from watchdog.observers import Observer


# ---------------------------------------- Create Flask app ----------------------------------------

app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    ),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
)

# ---------------------------------------- Define variables ----------------------------------------

sub_manager = SubscriptionManager()
embedding = FaceEmbeddingDB()
channel = "030326"
app.secret_key = os.urandom(24)

# ---------------------------------------- Thread to process frames ----------------------------------------

# Initialize the Camera object
camera = Camera(channel, camera_index=1)
cap = camera.start_camera()

# Start the video processing in a separate thread
video_processing_thread = Thread(target=camera.process_video, daemon=True)
video_processing_thread.start()


# ---------------------------------------- Routes ----------------------------------------


# ======= Main page for log in and sign up (index.html) =======
@app.route("/")
def index():
    return render_template("index.html")


app.add_url_rule("/validate_signIn", "validate_signIn", validate_signIn, methods=["POST"])
app.add_url_rule("/validate_signUp", "validate_signUp", validate_signUp, methods=["POST"])
app.add_url_rule("/update_password", "update_password", update_password, methods=["POST"])
app.add_url_rule("/upload_photo", "upload_photo", upload_photo, methods=["POST"])
app.add_url_rule("/process_embeddings", "process_embeddings", process_embeddings, methods=["POST"])
app.add_url_rule("/store_subscription_code", "store_subscription_code", store_subscription_code,methods=["POST"])
app.add_url_rule("/remove_subscription_code", "remove_subscription_code", remove_subscription_code, methods=["POST"])
app.add_url_rule("/add_chatID", "add_chatID", add_chatID, methods=["POST"])
app.add_url_rule("/delete_chatID", "delete_chatID", delete_chatID, methods=["POST"])
app.add_url_rule("/update_phoneNum", "update_phoneNum", update_phoneNum, methods=["POST"])

@app.route('/recent-activity-stream')
def recent_activity_stream():
    return camera.stream_recent_activity()

# ======= Home page for livestream (home.html) =======
@app.route("/home")
def home():
    subscription_code = session.get("subscription_code")
    if not subscription_code:
        return redirect(url_for("index"))
    return render_template("home.html")


# Route to stream video
@app.route("/stream_video")
def stream_video():
    return camera.stream_video()


# ======= History page (history.html) =======
@app.route("/history")
def history():
    subscription_code = session.get("subscription_code")
    if not subscription_code:
        return redirect(url_for("index"))

    # Retrieve the selected date from the query string
    selected_date = request.args.get("filter_date")

    video_list = []
    video_dir = os.path.join("static", "videos", subscription_code)

    if os.path.exists(video_dir):
        for video_file in os.listdir(video_dir):
            if video_file.endswith(".webm"):
                # Extract the timestamp from the filename
                timestamp_str = video_file.split(".")[0]
                timestamp = datetime.strptime(timestamp_str, "%y%m%d%H%M%S")

                # Format the timestamp to dd/MM/yy HH:mm:ss
                formatted_timestamp = timestamp.strftime("%d/%m/%y %H:%M:%S")

                # If a filter date is provided, filter the videos
                if selected_date:
                    filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
                    if timestamp.date() != filter_date:
                        continue  # Skip videos that don't match the filter date

                # Add the video to the list with its formatted timestamp and URL
                video_list.append(
                    {
                        "timestamp": formatted_timestamp,
                        "url": url_for(
                            "static",
                            filename=f"videos/{subscription_code}/{video_file}",
                        ),
                        "datetime": timestamp  # Store the actual datetime object for sorting
                    }
                )

    # Sort the video_list by the 'datetime' key in descending order (latest first)
    video_list.sort(key=lambda x: x["datetime"], reverse=True)

    # Remove the 'datetime' key from each dictionary after sorting, as it's not needed in the template
    for video in video_list:
        del video["datetime"]

    return render_template(
        "history.html", video_list=video_list, selected_date=selected_date
    )


@app.route("/videos/<subscription_code>/<filename>")
def serve_video(subscription_code, filename):
    return send_from_directory(
        f"static/videos/{subscription_code}", filename, mimetype="video/webm"
    )


def format_timestamp_from_filename(filename):
    """Convert timestamp in filename to readable format: Intrusion at dd/MM/yy hh:mm:ss"""
    try:
        # Extract the timestamp (yyMMddhhmmss) from the filename and convert it to a datetime object
        timestamp_str = filename.split(".")[0]
        timestamp = datetime.strptime(timestamp_str, "%y%m%d%H%M%S")
        return timestamp.strftime("%d/%m/%y %H:%M:%S")
    except ValueError:
        return "Invalid Timestamp"

# ======= User Account page (userAccount.html) =======
@app.route("/user_account")
def user_account():
    subscription_code = session.get("subscription_code")
    if not subscription_code:
        return redirect(url_for("index"))

    # Get chat IDs and associated phone numbers
    telegram_chat_ids = sub_manager.get_chat_ids_by_subscription_code(subscription_code)
    registered_name = embedding.get_registered_persons(subscription_code)

    return render_template(
        "userAccount.html",
        subscription_code=subscription_code,
        telegram_chat_ids=telegram_chat_ids,  # List of dictionaries with chat_id and phone_num
        registered_persons=registered_name,  
    )

# ---------------------------------------- Start Flask app ----------------------------------------


def start_flask_app():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    start_flask_app()
