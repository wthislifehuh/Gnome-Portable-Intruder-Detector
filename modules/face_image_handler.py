import os
from watchdog.events import FileSystemEventHandler
from deepface import DeepFace


class FaceImageHandler(FileSystemEventHandler):
    """Handler for file system events in the monitored directory"""

    def on_created(self, event):
        # Check if the new file is an image
        if event.src_path.endswith((".png", ".jpg", ".jpeg")):
            print(f"New image detected: {event.src_path}")
            # Extract face embedding
            self.process_image(event.src_path)

    def process_image(self, image_path):
        try:
            # Use DeepFace to extract the face embeddings from the image
            embedding = DeepFace.represent(img_path=image_path, model_name="Facenet")
            print(f"Embedding for {image_path}: {embedding}")
            # You can now save the embeddings to a database or use them as needed
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
