# Main entry point for the cybersecurity phishing training application
# This file starts the Flask development server

from app import app  # noqa: F401

if __name__ == '__main__':
    # Start the Flask application in debug mode for development
    app.run(host='0.0.0.0', port=5000, debug=True)
