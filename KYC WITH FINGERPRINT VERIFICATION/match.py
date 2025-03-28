import cv2
import sqlite3
import numpy as np
from utils.encryption import decrypt_data
from utils.logger import setup_logger

logger = setup_logger()

def preprocess_image(image_path):
    """
    Preprocess the fingerprint image (convert to grayscale and enhance contrast).
    """
    try:
        # Read the image in grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            logger.error(f"Failed to read image: {image_path}")
            return None

        # Enhance contrast using histogram equalization
        image = cv2.equalizeHist(image)

        # Apply Gaussian blur to reduce noise
        image = cv2.GaussianBlur(image, (5, 5), 0)

        logger.info("Image preprocessed successfully.")
        return image

    except Exception as e:
        logger.error(f"Error in preprocess_image: {e}")
        return None

def extract_features(image):
    """
    Extract SIFT features from the preprocessed image.
    """
    try:
        # Initialize SIFT detector
        sift = cv2.SIFT_create()

        # Detect keypoints and descriptors
        keypoints, descriptors = sift.detectAndCompute(image, None)
        if descriptors is None:
            logger.error("No descriptors found in the image.")
            return None

        logger.info(f"Extracted {len(descriptors)} descriptors.")
        return descriptors

    except Exception as e:
        logger.error(f"Error in extract_features: {e}")
        return None

def match_fingerprint(new_image_path):
    """
    Match a new fingerprint against stored fingerprints in the database.
    """
    try:
        # Preprocess the new image
        new_image = preprocess_image(new_image_path)
        if new_image is None:
            logger.error("New image preprocessing failed.")
            return "No match found"

        # Extract features from the new image
        new_descriptors = extract_features(new_image)
        if new_descriptors is None:
            logger.error("Feature extraction failed for the new image.")
            return "No match found"

        # Connect to the database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, descriptors, encryption_key FROM fingerprints")

        best_match = None
        bf = cv2.BFMatcher()
        max_matches = 0

        # Compare the new fingerprint with each stored fingerprint
        for name, stored_descriptors, key in cursor.fetchall():
            # Decrypt the stored descriptors
            stored_descriptors = np.frombuffer(decrypt_data(stored_descriptors, key), dtype=np.float32).reshape(-1, 128)

            # Match descriptors using the Brute-Force Matcher
            matches = bf.knnMatch(new_descriptors, stored_descriptors, k=2)

            # Apply ratio test to filter good matches
            good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

            # Update the best match if the current match is better
            if len(good_matches) > max_matches:
                max_matches = len(good_matches)
                best_match = name

        conn.close()

        # Apply a threshold to determine if the match is valid
        if best_match and max_matches > 10:  # Adjust the threshold as needed
            logger.info(f"Best match found: {best_match} with {max_matches} good matches.")
            return best_match
        else:
            logger.info("No match found.")
            return "No match found"

    except Exception as e:
        logger.error(f"Error in match_fingerprint: {e}")
        return "No match found"

if __name__ == "__main__":
    # Test the matching function
    test_image_path = "static/test_fingerprint.png"  # Replace with the path to a test image
    match_result = match_fingerprint(test_image_path)
    print(f"Match Result: {match_result}")