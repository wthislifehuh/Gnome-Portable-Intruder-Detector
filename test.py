import cv2


def start():
    # Open a connection to the default camera (usually the first camera)
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    return cap


def stream(cap):
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly, ret is True
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Display the resulting frame
        cv2.imshow("Camera Feed", frame)

        # Press 'q' to exit the video feed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


# Starting the camera
cap = start()

# If camera started successfully, begin streaming
if cap:
    stream(cap)
