import cv2
import time

# Initialize the background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# Open the video file
video_path = "media/quiet_room.mp4"
cap = cv2.VideoCapture(video_path)

# Variables to calculate FPS
frame_count = 0
start_time = time.time()
fps_sum = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply the background subtractor
    fg_mask = bg_subtractor.apply(frame)

    # Post-processing to remove noise
    fg_mask = cv2.morphologyEx(
        fg_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    )

    # Check for motion (if there are any non-zero pixels in the fg_mask)
    if cv2.countNonZero(fg_mask) > 0:
        print("Event Detected")
    else:
        print("No Event Detected")

    # Display the result
    cv2.imshow("Frame", frame)
    cv2.imshow("FG Mask", fg_mask)

    # Calculate FPS
    frame_count += 1
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time
    fps_sum += fps
    print(f"FPS: {fps:.2f}")

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Calculate and print average FPS
average_fps = fps_sum / frame_count
print(f"Average FPS: {average_fps:.2f}")

cap.release()
cv2.destroyAllWindows()
