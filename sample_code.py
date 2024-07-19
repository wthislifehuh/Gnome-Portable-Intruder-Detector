import cv2
import torch
from matplotlib import pyplot as plt 


# Load the model
model = torch.hub.load('ultralytics/yolov5','yolov5s', pretrained=True)

# Start the webcam video capture
cap = cv2.VideoCapture(1)

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()
    
    # If the frame was not read successfully, break the loop
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = model(rgb_frame)

    annotate_frame = cv2.cvtColor(results.render()[0],cv2.COLOR_RGB2BGR)

    cv2.imshow('Face Detection',  annotate_frame)
    
    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()