import cv2


class EventDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    def analyze_frame(self, roi):
        # Apply the background subtractor to the ROI
        fg_mask = self.bg_subtractor.apply(roi)

        # Post-processing to remove noise
        fg_mask = cv2.morphologyEx(
            fg_mask,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        )

        # Check for motion in the ROI
        event_detected = cv2.countNonZero(fg_mask) > 0

        return fg_mask, event_detected
