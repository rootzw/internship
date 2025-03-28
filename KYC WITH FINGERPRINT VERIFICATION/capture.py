import cv2
import numpy as np
from datetime import datetime
from utils.logger import setup_logger
import os

logger = setup_logger()

def capture_fingerprint():
    """
    Captures a fingerprint image from the webcam and saves it.
    Returns the file path of the saved image.
    """
    try:
        # Ensure the static directory exists
        if not os.path.exists("static"):
            os.makedirs("static")
            logger.info("Created 'static' directory.")

        # Open the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Failed to open webcam.")
            return None

        logger.info("Webcam opened successfully. Press 's' to capture the fingerprint.")

        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to capture frame.")
                break

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Fingerprint Capture", gray)

            # Save the image when 's' is pressed
            if cv2.waitKey(1) & 0xFF == ord('s'):
                filename = f"static/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                cv2.imwrite(filename, gray)
                logger.info(f"Fingerprint saved as {filename}")

                # Display a confirmation message on the screen
                cv2.putText(gray, "Fingerprint Captured!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Fingerprint Capture", gray)
                cv2.waitKey(2000)  # Display the message for 2 seconds
                break

        # Release the webcam and close the window
        cap.release()
        cv2.destroyAllWindows()
        return filename

    except Exception as e:
        logger.error(f"Error in capture_fingerprint: {e}")
        return None

if __name__ == "__main__":
    # Test the capture function
    image_path = capture_fingerprint()
    if image_path:
        print(f"Fingerprint captured and saved at: {image_path}")
    else:
        print("Failed to capture fingerprint.")