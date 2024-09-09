import cv2


class EventDetector:
    def __init__(self, min_area_threshold=2000):
        # Background subtractor initialization
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        # Minimum number of non-zero pixels (area) to consider an event
        self.min_area_threshold = min_area_threshold

    def analyze_frame(self, frame):
        # Apply the background subtractor to the frame
        fg_mask = self.bg_subtractor.apply(frame)

        # Post-processing to remove noise (morphological opening)
        fg_mask = cv2.morphologyEx(
            fg_mask,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        )

        # Count non-zero pixels (movement) in the foreground mask
        non_zero_count = cv2.countNonZero(fg_mask)

        # Check if the detected movement is larger than the defined threshold
        event_detected = non_zero_count > self.min_area_threshold

        return fg_mask, event_detected
