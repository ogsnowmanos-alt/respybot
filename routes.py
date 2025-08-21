import logging
from flask import render_template, jsonify, request
from app import app
from bot import get_bot_status

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page showing bot status and information"""
    try:
        bot_status = get_bot_status()
        return render_template('index.html', bot_status=bot_status)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return render_template('index.html', bot_status={'connected': False, 'error': str(e)})

@app.route('/bot-status')
def bot_status_page():
    """Detailed bot status page"""
    try:
        bot_status = get_bot_status()
        return render_template('bot_status.html', bot_status=bot_status)
    except Exception as e:
        logger.error(f"Error rendering bot status page: {e}")
        return render_template('bot_status.html', bot_status={'connected': False, 'error': str(e)})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        bot_status = get_bot_status()
        return jsonify({
            'status': 'healthy',
            'flask_server': 'running',
            'discord_bot': 'connected' if bot_status['connected'] else 'disconnected',
            'bot_details': bot_status
        })
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'status': 'error',
            'flask_server': 'running',
            'discord_bot': 'error',
            'error': str(e)
        }), 500

@app.route('/api/bot-status')
def api_bot_status():
    """API endpoint for bot status"""
    try:
        return jsonify(get_bot_status())
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return render_template('index.html', error="Internal server error"), 500
