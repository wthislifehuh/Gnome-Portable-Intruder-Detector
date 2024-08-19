import cv2
import os


# Function to create directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Initialize video capture from the first camera (usually the default camera)
cap = cv2.VideoCapture(0)

# Directory to save frames
username = "kenhow"
output_dir = f"face_recognition/{username}"
create_directory(output_dir)

# Frame rate (number of frames to skip)
frame_rate = 15  # Save one frame every 5 frames

# Initialize a counter to keep track of frames
frame_count = 0

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Only save every nth frame (based on frame_rate)
    if frame_count % frame_rate == 0:
        frame_name = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_name, frame)
        print(f"Saved: {frame_name}")

    # Display the resulting frame
    cv2.imshow("Video", frame)

    # Press 'q' to exit the video capturing loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Increment the frame count
    frame_count += 1

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
