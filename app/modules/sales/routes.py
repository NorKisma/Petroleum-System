from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Sale, SaleReturn, SaleItem, Customer, Branch
from app.services.sale_service import SaleService
from app.utils.audit import log_audit
from app import db
from datetime import datetime

sales = Blueprint('sales', __name__)

@sales.route('/sales')
@login_required
def list_sales():
    all_sales = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all()
    return render_template('sales/index.html', sales=all_sales)

@sales.route('/sales/returns')
@login_required
def list_returns():
    returns = SaleReturn.query.filter_by(tenant_id=current_user.tenant_id).order_by(SaleReturn.created_at.desc()).all()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Fetch recent sales for the dropdown (last 100 sales)
    recent_sales = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).limit(100).all()
    return render_template('sales/returns.html', returns=returns, customers=customers, recent_sales=recent_sales)

@sales.route('/pos')
@login_required
def pos():
    from app.models import Customer, Category, ChartAccount
    products = Product.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    # Professional Accounting: Fetch Payment Accounts
    asset_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    receivable_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', sub_category='Accounts Receivable', is_active=True).all()
    
    return render_template('sales/pos.html', 
                           products=products, 
                           customers=customers, 
                           categories=categories,
                           asset_accounts=asset_accounts,
                           receivable_accounts=receivable_accounts)

@sales.route('/pos/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    items = data.get('items')
    total_amount = data.get('total_amount')
    payment_method = data.get('payment_method', 'Cash')
    customer_id = data.get('customer_id')
    
    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty!'})

    try:
        # Use our Backend Service to process the logic
        new_sale = SaleService.process_sale(
            items=items,
            total_amount=total_amount,
            payment_method=payment_method,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            customer_id=customer_id
        )
        
        log_audit('SALE_CHECKOUT', 'SALES', f'Processed sale: {new_sale.invoice_no} (Total: {total_amount})')
        
        return jsonify({
            'success': True, 
            'message': 'Iibka waa lagu guulaystay!', 
            'invoice_no': new_sale.invoice_no
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@sales.route('/invoice/<invoice_no>')
@login_required
def invoice_view(invoice_no):
    sale = Sale.query.filter_by(invoice_no=invoice_no, tenant_id=current_user.tenant_id).first_or_404()
    return render_template('sales/invoice.html', sale=sale)

# --- Returns API & Processing ---
@sales.route('/get-invoice-data/<invoice_no>')
@login_required
def get_sale_by_invoice(invoice_no):
    sale = Sale.query.filter_by(invoice_no=invoice_no, tenant_id=current_user.tenant_id).first()
    if not sale:
        return jsonify({'success': False, 'message': 'Invoice-kan lama helin.'})
    
    return jsonify({
        'success': True,
        'sale_id': sale.id,
        'invoice_no': sale.invoice_no,
        'total_amount': sale.total_amount,
        'customer': sale.customer.name if sale.customer else 'Walk-In'
    })

@sales.route('/return/process/<int:sale_id>')
@login_required
def return_process(sale_id):
    sale = Sale.query.filter_by(id=sale_id, tenant_id=current_user.tenant_id).first_or_404()
    reason = request.args.get('reason', 'Damaged Product')
    return render_template('sales/process_return.html', sale=sale, reason=reason)
