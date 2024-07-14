import cv2
import time

# Open the video file
video_path = "media/quiet_room.mp4"
cap = cv2.VideoCapture(video_path)

# Read the first frame
ret, frame1 = cap.read()
if not ret:
    print("Failed to read the video")
    cap.release()
    exit()

# Convert the first frame to grayscale
prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

# Variables to calculate FPS
frame_count = 0
start_time = time.time()
fps_sum = 0

while True:
    ret, frame2 = cap.read()
    if not ret:
        break

    # Convert the current frame to grayscale
    gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the current frame and the previous frame
    diff = cv2.absdiff(prev_gray, gray)

    # Threshold the difference image
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Post-processing to remove noise
    thresh = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    )

    # Check for motion (if there are any non-zero pixels in the thresh image)
    if cv2.countNonZero(thresh) > 0:
        print("Event Detected")
    else:
        print("No Event Detected")

    # Display the result
    cv2.imshow("Frame", frame2)
    cv2.imshow("Motion Detection", thresh)

    # Calculate FPS
    frame_count += 1
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time
    fps_sum += fps
    print(f"FPS: {fps:.2f}")

    # Update the previous frame
    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Calculate and print average FPS
average_fps = fps_sum / frame_count
print(f"Average FPS: {average_fps:.2f}")

cap.release()
cv2.destroyAllWindows()
