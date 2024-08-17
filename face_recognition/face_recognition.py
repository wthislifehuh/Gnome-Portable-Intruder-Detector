# pip install deepface opencv-python tf-keras
# ================================================================
# WORKING VERSION
# ================================================================

import cv2
from deepface import DeepFace
import os
import logging
import re

# Suppress DeepFace logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# Define the database path where images are stored
db_path = "./face_recognition/faces/"

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    try:
        # Detect faces in the frame
        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_detector.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5)

        for x, y, w, h in faces:
            # Crop the face area from the frame
            face_img = frame[y : y + h, x : x + w]

            # Perform face recognition on the cropped face
            recognition = DeepFace.find(
                img_path=face_img,
                model_name="Facenet512",
                db_path=db_path,
                enforce_detection=False,
                silent=True,
            )

            print(recognition)
            # Perform analysis
            # results = DeepFace.analyze(frame, actions=['emotion', 'age', 'gender', 'race'])
            # To access results: eg. results["age"]

            # Determine identity
            if recognition and not recognition[0].empty:
                filename = (
                    recognition[0]["identity"].values[0].split("/")[-1]
                )  # Get the filename, e.g., 'joe_ee2.jpg'
                # Remove the file extension
                name_without_extension = os.path.splitext(filename)[0]  # Get 'joe_ee2'
                # Remove digits from the name
                name_without_numbers = re.sub(
                    r"\d+", "", name_without_extension
                )  # Get 'joe_ee'
                # Replace underscores with spaces and capitalize each word
                identity = name_without_numbers.replace(
                    "_", " "
                ).title()  # Get 'Joe Ee'
            else:
                identity = "Unknown"

            print(identity)

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Prepare the text to display
            text = f"Name: {identity}"

            # Calculate text size
            (text_width, text_height), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )

            # Ensure text is above the face rectangle
            y_text = y - 10 if y - 10 > text_height else y + h + text_height + 10

            # Overlay the text above the face
            cv2.putText(
                frame,
                text,
                (x, y_text),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

    except Exception as e:
        print("Error in analyzing frame:", str(e))

    # Display the resulting frame
    cv2.imshow("Webcam", frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()


# =========================== TESTING VERSION =====================================
# import cv2
# from deepface import DeepFace

# # Define the database path where images are stored
# db_path = "./human_recognition/faces/"
# # Predefined image for identity matching
# img_path = "joe_ee.jpg"

# models = [
#   "VGG-Face",
#   "Facenet",
#   "Facenet512",
#   "OpenFace",
#   "DeepFace",
#   "DeepID",
#   "ArcFace",
#   "Dlib",
#   "SFace",
#   "GhostFaceNet",
# ]

# # This function will be called every time a frame is captured
# def recognize_face(frame):
#     try:
#         # Perform real-time face recognition and return analysis results
#         results = DeepFace.analyze(frame, actions=['emotion', 'age',  'gender', 'race'])

#         # Perform face recognition
#         recognition = DeepFace.find(img_path=frame, db_path=db_path, model_name= models[2])
#         if len(recognition) > 0:
#             identity = recognition[0]["identity"].values[0].split('/')[-2]
#         else:
#             identity = "Unknown"

#         print(identity)
#         # Display the results on the frame
#         cv2.putText(frame, f'Name: {identity}', (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Age: {int(results["age"])}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Gender: {results["gender"]}', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Emotion: {results["dominant_emotion"]}', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

#     except Exception as e:
#         print("Error in analyzing frame:", str(e))

#     return frame

# # Start webcam and analyze frames
# DeepFace.stream(db_path=db_path, model_name = models[2], source=0, time_threshold=5)


# # To end the stream, press 'q' on the webcam window


# =========================== TESTING VERSION =====================================
# WORKING MODULES using Deepface and webcam

# models = [
#   "VGG-Face",
#   "Facenet",
#   "Facenet512",
#   "OpenFace",
#   "DeepFace",
#   "DeepID",
#   "ArcFace",
#   "Dlib",
#   "SFace",
#   "GhostFaceNet",
# ]

# import cv2
# from deepface import DeepFace
# import os

# # Define the database path where images are stored
# db_path = "./human_recognition/faces/"

# # Predefined image for identity matching
# img_path = "joe_ee.jpg"

# # Open the webcam
# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         print("Failed to capture image")
#         break

#     try:
#         # Perform face recognition
#         recognition = DeepFace.find(img_path=frame, model_name= models[2],  db_path=db_path)
#         if len(recognition) > 0:
#             filename = recognition[0]["identity"].values[0].split('/')[-1]  # Get 'joe_ee.jpg'
#             # Remove the file extension
#             name_without_extension = os.path.splitext(filename)[0]  # Get 'joe_ee'
#             # Replace underscores with spaces and capitalize each word
#             identity = name_without_extension.replace('_', ' ').title()  # Get 'Joe Ee'

#         else:
#             identity = "Unknown"

#         print(identity)

#         # Perform analysis
#         results = DeepFace.analyze(frame, actions=['emotion', 'age', 'gender', 'race'])

#         # Display the results on the frame
#         cv2.putText(frame, f'Name: {identity}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Age: {int(results["age"])}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Gender: {results["gender"]}', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(frame, f'Emotion: {results["dominant_emotion"]}', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

#     except Exception as e:
#         print("Error in analyzing frame:", str(e))

#     # Display the resulting frame
#     cv2.imshow('Webcam', frame)

#     # Break the loop when 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break


# ============================ TESTING VERSION =====================================
# # # Release the capture and close windows
# # cap.release()
# # cv2.destroyAllWindows()

# import cv2
# from deepface import DeepFace
# import os
# import logging
# import re

# # Suppress DeepFace logging
# logging.getLogger('tensorflow').setLevel(logging.ERROR)

# # Define the database path where images are stored
# db_path = "./human_recognition/faces/"

# # Open the webcam
# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         print("Failed to capture image")
#         break

#     try:
#         # Perform face recognition
#         recognition = DeepFace.find(img_path=frame, model_name="Facenet512", db_path=db_path, enforce_detection= False, silent=True)
#         print(recognition)

#         # Check if recognition list is not empty
#         if len(recognition) > 0 and len(recognition[0]) > 0:
#             filename = recognition[0]["identity"].values[0].split('/')[-1]  # Get 'joe_ee2.jpg'
#             # Remove the file extension
#             name_without_extension = os.path.splitext(filename)[0]  # Get 'joe_ee2'

#             # Remove digits from the name
#             name_without_numbers = re.sub(r'\d+', '', name_without_extension)  # Get 'joe_ee'

#             # Replace underscores with spaces and capitalize each word
#             identity = name_without_numbers.replace('_', ' ').title()  # Get 'Joe Ee'
#         else:
#             identity = "Unknown"

#         print(identity)

#         # Perform analysis (currently commented out)
#         # results = DeepFace.analyze(frame, actions=['age', 'gender', 'race'])
#         # print(results)

#         # Detect faces in the frame
#         face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#         faces = face_detector.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5)

#         for (x, y, w, h) in faces:
#             # Draw a rectangle around the face
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#             # Prepare the text to display
#             text = f'Name: {identity}'
#             # \nAge: {int(results["age"])} \nRace: {results["race"]} \nGender: {results["gender"]}

#             # Calculate text size
#             (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

#             # Ensure text is above the face rectangle
#             y_text = y - 10 if y - 10 > text_height else y + h + text_height + 10

#             # Draw background rectangle for text
#             # cv2.rectangle(frame, (x, y_text - text_height - 10), (x + text_width, y_text + 5), (0, 255, 0), -1)

#             # Overlay the text above the face
#             cv2.putText(frame, text, (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

#     except Exception as e:
#         print("Error in analyzing frame:", str(e))


#     # Display the resulting frame
#     cv2.imshow('Webcam', frame)

#     # Break the loop when 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the capture and close windows
# cap.release()
# cv2.destroyAllWindows()
