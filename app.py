import os
import time
import requests
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get configuration from environment variables
TARGET_URL = os.getenv('TARGET_URL')
if not TARGET_URL:
    raise ValueError("TARGET_URL environment variable must be set")

CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds
ACCEPTED_STATUS_CODES = [int(x) for x in os.getenv('ACCEPTED_STATUS_CODES', '200').split(',')]

# Proxy configuration
HTTP_PROXY = os.getenv('HTTP_PROXY')
HTTPS_PROXY = os.getenv('HTTPS_PROXY')

# Configure proxy settings
proxies = {}
if HTTP_PROXY:
    proxies['http'] = HTTP_PROXY
if HTTPS_PROXY:
    proxies['https'] = HTTPS_PROXY

# Global variable to store the last check result
last_check = "NA"

def check_site():
    """
    Performs the actual site connectivity check
    """
    global last_check
    
    while True:
        try:
            start_time = time.time()
            response = requests.get(
                TARGET_URL, 
                timeout=10,
                proxies=proxies,
                verify=True
            )
            response_time = time.time() - start_time
            
            status = 'OK' if response.status_code in ACCEPTED_STATUS_CODES else 'NOK'
            last_check = status
            
            details = {
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'error': None,
                'using_proxy': bool(proxies),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Check result: {status}\n"
                f"Details: {json.dumps(details, indent=2)}\n"
                f"Target URL: {TARGET_URL}\n"
                f"Accepted status codes: {ACCEPTED_STATUS_CODES}"
            )
            
        except requests.RequestException as e:
            last_check = 'NOK'
            
            details = {
                'status_code': None,
                'response_time': None,
                'error': str(e),
                'using_proxy': bool(proxies),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.error(
                f"Check failed\n"
                f"Details: {json.dumps(details, indent=2)}\n"
                f"Target URL: {TARGET_URL}"
            )
            
        time.sleep(CHECK_INTERVAL)

@app.route('/status')
def status():
    """
    Returns the status of the last check
    """
    return last_check

def main():
    # Log initial configuration
    logger.info(
        f"Starting monitor with configuration:\n"
        f"Target URL: {TARGET_URL}\n"
        f"Check interval: {CHECK_INTERVAL}s\n"
        f"Accepted status codes: {ACCEPTED_STATUS_CODES}\n"
        f"Using proxy: {bool(proxies)}"
    )
    if proxies:
        logger.info(f"Proxy configuration: {json.dumps(proxies, indent=2)}")

    # Start the monitoring thread
    monitor_thread = Thread(target=check_site, daemon=True)
    monitor_thread.start()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
