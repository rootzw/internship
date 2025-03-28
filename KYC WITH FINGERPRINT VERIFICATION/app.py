from flask import Flask, render_template, request
from capture import capture_fingerprint
from train import store_fingerprint
from match import match_fingerprint
from utils.logger import setup_logger

# Set up logging
logger = setup_logger()

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the main page with the fingerprint recognition UI.
    """
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    """
    Handles fingerprint training (capture and store).
    """
    try:
        # Get the name from the form
        name = request.form['name']
        logger.info(f"Training fingerprint for user: {name}")

        # Capture a new fingerprint
        image_path = capture_fingerprint()
        if not image_path:
            logger.error("Failed to capture fingerprint.")
            return "Error capturing fingerprint. Check logs for details."

        # Store the fingerprint in the database
        if store_fingerprint(name, image_path):
            logger.info(f"Fingerprint stored successfully for {name}.")
            return "Fingerprint Stored!"
        else:
            logger.error("Failed to store fingerprint.")
            return "Error storing fingerprint. Check logs for details."

    except Exception as e:
        logger.error(f"Error in /train route: {e}")
        return "An error occurred. Check logs for details."

@app.route('/recognize', methods=['POST'])
def recognize():
    """
    Handles fingerprint recognition (capture and match).
    """
    try:
        logger.info("Recognizing fingerprint...")

        # Capture a new fingerprint
        image_path = capture_fingerprint()
        if not image_path:
            logger.error("Failed to capture fingerprint.")
            return "Error capturing fingerprint. Check logs for details."

        # Match the fingerprint against the database
        match_result = match_fingerprint(image_path)
        logger.info(f"Match result: {match_result}")
        return render_template('index.html', match_result=match_result)

    except Exception as e:
        logger.error(f"Error in /recognize route: {e}")
        return "An error occurred. Check logs for details."

if __name__ == "__main__":
    # Run the Flask app
    logger.info("Starting Flask application...")
    app.run(debug=True)