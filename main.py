import logging
import threading
import time
from app import app
from bot import run_discord_bot

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_flask():
    """Run the Flask web server"""
    logger.info("Starting Flask server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    """Main function to start both Flask and Discord bot concurrently"""
    logger.info("Starting Discord bot with Flask backend")
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server thread started")
    
    # Give Flask a moment to start
    time.sleep(1)
    
    # Start Discord bot (this will block)
    logger.info("Starting Discord bot")
    run_discord_bot()

if __name__ == "__main__":
    main()
