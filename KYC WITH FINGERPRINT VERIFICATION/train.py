import cv2
import sqlite3
import numpy as np
from utils.encryption import encrypt_data, generate_key
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

def store_fingerprint(name, image_path):
    """
    Store fingerprint features in the database after encryption.
    """
    try:
        # Preprocess the image
        image = preprocess_image(image_path)
        if image is None:
            logger.error("Image preprocessing failed.")
            return False

        # Extract features
        descriptors = extract_features(image)
        if descriptors is None:
            logger.error("Feature extraction failed.")
            return False

        # Encrypt descriptors
        key = generate_key()
        encrypted_descriptors = encrypt_data(descriptors.tobytes(), key)

        # Store in SQLite database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY,
                name TEXT,
                image_path TEXT,
                descriptors BLOB,
                encryption_key BLOB
            )
        """)
        cursor.execute("""
            INSERT INTO fingerprints (name, image_path, descriptors, encryption_key)
            VALUES (?, ?, ?, ?)
        """, (name, image_path, encrypted_descriptors, key))
        conn.commit()
        conn.close()

        logger.info(f"Fingerprint stored for {name}.")
        return True

    except Exception as e:
        logger.error(f"Error in store_fingerprint: {e}")
        return False

if __name__ == "__main__":
    # Test the train function
    name = input("Enter name: ")
    image_path = "static/temp_fingerprint.png"  # Replace with the path to a test image
    if store_fingerprint(name, image_path):
        print("Fingerprint stored successfully.")
    else:
        print("Failed to store fingerprint.")