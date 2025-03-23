from flask import Flask, request, jsonify
import requests
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linkedin_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directory to store received profiles
PROFILES_DIR = "linkedin_profiles"
os.makedirs(PROFILES_DIR, exist_ok=True)

@app.route('/webhook/clay-callback', methods=['POST'])
def clay_callback():
    """
    Endpoint to receive webhook callbacks from Clay
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        profile_id = data.get('url', '').split('/')[-1] if 'url' in data else 'unknown'
        filename = f"{profile_id}_{timestamp}.json"
        file_path = os.path.join(PROFILES_DIR, filename)
        
        # Save the profile data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Received and saved profile data via webhook: {filename}")
        
        return jsonify({
            "status": "success", 
            "message": "Profile data received and saved", 
            "file": filename
        })
    
    except Exception as e:
        logger.error(f"Error handling webhook callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({"status": "ok", "message": "LinkedIn service is running"})

def start_service(port=8080):
    """
    Start the Flask service
    
    Args:
        port: Port number to run the service on
    """
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)