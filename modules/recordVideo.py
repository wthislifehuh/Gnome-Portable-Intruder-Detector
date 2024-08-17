# FOR REFERENCE, INTEGRATED IN CAMERA


import cv2
import os
import time

def record_video(trigger, output_filename="intruder.mp4"):
    # Define the path where the video will be saved
    output_dir = os.path.join(os.getcwd(), 'assets', 'videos')
    os.makedirs(output_dir, exist_ok=True)
    output_filepath = os.path.join(output_dir, output_filename)

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    # Define the codec and create a VideoWriter objcvfgvvcvcect
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    out = None
    
    while True:
        if trigger():
            if out is None:
                # Get the width and height of the frame
                frame_width = int(cap.get(3))
                frame_height = int(cap.get(4))
                out = cv2.VideoWriter(output_filepath, fourcc, 20.0, (frame_width, frame_height))
                print("Recording started...")
            
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                # Write the frame to the file
                out.write(frame)
                # Display the frame (optional)
                cv2.imshow('Recording', frame)
            else:
                break
        else:
            if out is not None:
                print("Recording stopped.")
                break
        
        # Stop recording if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Recording stopped by user.")
            break
    
    # Release the capture and writer objects
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

# Example trigger function
def trigger():
    # In a real scenario, replace this with the actual condition
    # Here we simulate the input with time for demonstration
    return time.time() % 10 < 5  # Recording for 5 seconds every 10 seconds

# Usage
record_video(trigger)

