"""
API Routes — Petroleum Management System
Secured with X-API-Key header authentication.

Usage:
    Add header:  X-API-Key: <your-api-key>
    Set in .env: API_SECRET_KEY=your-long-random-key
"""

import functools
from flask import Blueprint, jsonify, request, current_app
import secrets

api = Blueprint('api', __name__)


# ─── API Key Authentication Decorator ─────────────────────────────────────────

def require_api_key(f):
    """
    Decorator that enforces X-API-Key header authentication.
    Key must match API_SECRET_KEY in app config / .env
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key', '').strip()
        expected_key = current_app.config.get('API_SECRET_KEY', '')

        if not expected_key:
            # If no API key is configured, deny all access for safety
            return jsonify({
                'success': False,
                'error': 'API not configured. Set API_SECRET_KEY in your .env file.'
            }), 503

        if not provided_key or not secrets.compare_digest(provided_key, expected_key):
            return jsonify({
                'success': False,
                'error': 'Unauthorized. Provide a valid X-API-Key header.'
            }), 401

        return f(*args, **kwargs)
    return decorated


# ─── Public Health Check (no auth needed) ────────────────────────────────────

@api.route('/api/health')
def health_check():
    """Public endpoint to verify the API is running."""
    return jsonify({
        'status': 'ok',
        'version': '1.0',
        'message': 'Petroleum API is running'
    })
