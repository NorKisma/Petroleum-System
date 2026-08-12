"""
API Routes — Advanced Inventory POS & Accounting System
Secured with X-API-Key header authentication.

Usage:
    Add header:  X-API-Key: <your-api-key>
    Set in .env: API_SECRET_KEY=your-long-random-key
"""

import functools
from flask import Blueprint, jsonify, request, current_app
from app.models import Product, Sale, Tenant
from app.services.sale_service import SaleService
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
        'message': 'Advanced POS API is running'
    })


# ─── Products Endpoint ────────────────────────────────────────────────────────

@api.route('/api/products', methods=['GET'])
@require_api_key
def get_products():
    """
    Get all products for a tenant.
    Requires: X-API-Key header + tenant_id query param
    Example: GET /api/products?tenant_id=1
    """
    tenant_id = request.args.get('tenant_id', type=int)
    if not tenant_id:
        return jsonify({'success': False, 'error': 'tenant_id is required'}), 400

    # Verify tenant exists
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'success': False, 'error': 'Tenant not found'}), 404

    products = Product.query.filter_by(tenant_id=tenant_id, is_active=True).all()

    return jsonify({
        'success': True,
        'count': len(products),
        'products': [{
            'id':       p.id,
            'name':     p.name,
            'price':    p.sell_price,
            'stock':    p.stock_quantity,
            'barcode':  p.barcode,
            'category': p.category.name if p.category else None
        } for p in products]
    })


# ─── Checkout Endpoint ────────────────────────────────────────────────────────

@api.route('/api/checkout', methods=['POST'])
@require_api_key
def api_checkout():
    """
    Process a sale via API (for mobile app or kiosk integration).
    Requires: X-API-Key header
    Body: {
        "items": [{"product_id": 1, "quantity": 2, "unit_price": 10.0, "buy_price": 6.0}],
        "total_amount": 20.0,
        "payment_method": "Mobile",
        "user_id": 1,
        "tenant_id": 1
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON body provided'}), 400

    required = ['items', 'total_amount', 'user_id', 'tenant_id']
    missing  = [k for k in required if k not in data]
    if missing:
        return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400

    try:
        new_sale = SaleService.process_sale(
            items=data['items'],
            total_amount=data['total_amount'],
            payment_method=data.get('payment_method', 'Mobile'),
            user_id=data['user_id'],
            tenant_id=data['tenant_id']
        )
        return jsonify({
            'success': True,
            'invoice_no': new_sale.invoice_no,
            'total_amount': new_sale.total_amount
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ─── AI Invoice Scan Endpoint ─────────────────────────────────────────────────

@api.route('/api/ai/scan-invoice', methods=['POST'])
@require_api_key
def scan_invoice():
    """
    Upload an invoice image for AI extraction.
    Requires: X-API-Key header + multipart file upload (key: 'image')
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    import os, time
    from werkzeug.utils import secure_filename

    upload_dir = os.path.join('app', 'static', 'uploads', 'invoices')
    os.makedirs(upload_dir, exist_ok=True)

    filename  = secure_filename(f"invoice_{int(time.time())}_{file.filename}")
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # Simulated AI extraction (replace with real OCR/ML later)
    time.sleep(0.5)

    return jsonify({
        'success':     True,
        'invoice_no':  'INV-AI-' + str(int(time.time()))[-4:],
        'attachment':  f"uploads/invoices/{filename}",
        'items': [
            {'name': 'Sample Product 1', 'qty': 10, 'cost': 15.0},
            {'name': 'Sample Product 2', 'qty': 5,  'cost': 25.0}
        ],
        'total': 275.0
    })
