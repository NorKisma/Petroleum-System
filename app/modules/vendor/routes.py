from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Vendor, Product, Purchase, PurchaseItem, VendorPayment, BankAccount, ChartAccount, Category
from app import db
from app.utils.decorators import roles_required
import uuid
from datetime import datetime

vendor = Blueprint('vendor', __name__)

@vendor.route('/vendor')
@login_required
def list_vendors():
    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('vendor/index.html', vendors=vendors)

@vendor.route('/vendor/add', methods=['POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def add_vendor():
    data = request.get_json()
    try:
        new_vendor = Vendor(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_vendor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alaab-keenaha waa la kaydiyay!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/purchases', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'accountant', 'developer')
def purchases():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        vendor_id = data.get('vendor_id')
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'credit').upper() # 'CASH', 'CREDIT', 'BANK'
        bank_account_id = data.get('bank_account_id')
        
        # If it's a bank payment, the 'ap_account' field will store the bank account ID
        # If it's credit, it stores the selected AP account (if any)
        payment_account = bank_account_id if payment_method == 'BANK' else data.get('ap_account')
        
        date_str = data.get('date')
        
        if not vendor_id or not items:
            return jsonify({'success': False, 'message': 'Vendor and items are required'}), 400
            
        try:
            purchase_date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            purchase_date = datetime.utcnow()
            
        total_amount = sum(float(item.get('unit_cost', 0)) * int(item.get('qty', 0)) for item in items)
        
        custom_invoice_no = data.get('invoice_no', '').strip()
        auto_invoice_no = f"{payment_method}-{str(uuid.uuid4())[:8].upper()}"
        invoice_no = custom_invoice_no if custom_invoice_no else auto_invoice_no

        # Check if the account has sufficient balance (unless On Credit)
        from app.services.accounting_service import AccountingService
        if payment_method.upper() != 'CREDIT':
            check_account_id = None
            if payment_method.upper() == 'CASH':
                cash_acc = AccountingService.get_account('Cash', current_user.tenant_id)
                if cash_acc:
                    check_account_id = cash_acc.id
            elif payment_method.upper() == 'BANK' and payment_account:
                check_account_id = payment_account
                
            if check_account_id:
                balance = AccountingService.get_account_balance(check_account_id, current_user.tenant_id)
                if balance < total_amount:
                    return jsonify({'success': False, 'message': f'Cilad! Akoonka kuguma filna. Haraagu waa ${balance:,.2f}'}), 400

        # Create Purchase
        new_purchase = Purchase(
            invoice_no=invoice_no,
            total_amount=total_amount,
            payment_method=payment_method,
            ap_account=payment_account, # Stores ID of Bank or AP account
            vendor_id=vendor_id,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            attachment=data.get('attachment'),
            purchase_date=purchase_date
        )
        db.session.add(new_purchase)
        db.session.flush() # Get ID
        
        # Add items and update inventory
        for item_data in items:
            prod_id = item_data.get('product_id')
            qty = int(item_data.get('qty', 0))
            unit_cost = float(item_data.get('unit_cost', 0))
            sell_price = float(item_data.get('selling_price', 0))
            
            product = None
            if prod_id:
                product = Product.query.get(prod_id)
            
            p_item = PurchaseItem(
                purchase_id=new_purchase.id,
                product_id=prod_id,
                product_name=product.name if product else "Unknown Product",
                quantity=qty,
                unit_cost=unit_cost,
                selling_price=sell_price,
                size=item_data.get('size')
            )
            db.session.add(p_item)
            
            if product:
                product.stock_quantity += qty
                product.buy_price = unit_cost
                if sell_price > 0:
                    product.sell_price = sell_price
                    
        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_purchase(new_purchase)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase saved successfully!'})

    # GET request - show list
    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Get accounts from Chart of Accounts
    accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Fallback to BankAccount if no ChartAccounts exist (legacy support)
    if not accounts:
        accounts = BankAccount.query.filter_by(tenant_id=current_user.tenant_id).all()
    purchases_list = Purchase.query.filter_by(tenant_id=current_user.tenant_id).order_by(Purchase.created_at.desc()).all()
    
    total_qty = 0
    total_cost = 0
    total_sales = 0
    purchase_data = []
    
    for p in purchases_list:
        p_qty = sum(item.quantity for item in p.items)
        p_cost = sum(item.quantity * item.unit_cost for item in p.items)
        p_sales = sum(item.quantity * (item.selling_price or 0) for item in p.items)
        names = ", ".join([item.product_name for item in p.items])
        
        total_qty += p_qty
        total_cost += p_cost
        total_sales += p_sales
        
        serialized_items = [{
            'name': item.product_name,
            'size': item.size,
            'qty': item.quantity,
            'cost_price': item.unit_cost,
            'selling_price': item.selling_price,
            'total_cost': item.quantity * item.unit_cost,
            'total_selling': item.quantity * (item.selling_price or 0)
        } for item in p.items]
            
        purchase_data.append({
            'obj': p,
            'invoice_no': p.invoice_no,
            'vendor_name': p.vendor.name if p.vendor else 'Unknown',
            'date': p.purchase_date.strftime('%d/%m/%Y') if p.purchase_date else p.created_at.strftime('%d/%m/%Y'),
            'names': names,
            'qty': p_qty,
            'cost_price': p_cost / p_qty if p_qty > 0 else 0,
            'selling_price': p_sales / p_qty if p_qty > 0 else 0,
            'total_cost': p_cost,
            'total_sales': p_sales,
            'profit': p_sales - p_cost,
            'serialized_items': serialized_items
        })
        
    summary = {
        'total_qty': total_qty,
        'total_cost': total_cost,
        'total_sales': total_sales,
        'profit': total_sales - total_cost
    }
    
    return render_template('vendor/purchases.html', 
                          vendors=vendors, 
                          products=products, 
                          categories=categories,
                          accounts=accounts,
                          purchases=purchase_data, 
                          summary=summary)

@vendor.route('/vendor/purchase/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    if purchase.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Reverse inventory changes and delete items
        items = PurchaseItem.query.filter_by(purchase_id=purchase.id).all()
        for item in items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity -= item.quantity
            db.session.delete(item) # Explicitly delete the item
        
        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(purchase.invoice_no, current_user.tenant_id)
        
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase deleted and inventory adjusted!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/purchase/return/<int:id>', methods=['POST'])
@login_required
def return_purchase(id):
    from app.models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem, Product
    purchase = Purchase.query.get_or_404(id)
    if purchase.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    qty = data.get('qty', 0)
    company = data.get('company', 'N/A')
    inv_no = data.get('inv_no', purchase.invoice_no)
    reason_text = data.get('reason', 'Damaged / Wrong Items')
    
    # Format a detailed reason string since the model doesn't have extra columns yet
    full_reason = f"[Qty: {qty}] [Co: {company}] [Inv: {inv_no}] {reason_text}"
    
    try:
        # 1. Create Purchase Return Header
        purchase_return = PurchaseReturn(
            purchase_id=purchase.id,
            invoice_no=inv_no,
            total_amount=0, # Will calculate based on items
            reason=full_reason,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(purchase_return)
        
        # 2. Process Specific Product Return
        selected_product_name = data.get('product')
        return_qty = int(qty)
        
        if selected_product_name:
            # Find the item in this purchase
            item = PurchaseItem.query.filter_by(purchase_id=purchase.id, product_name=selected_product_name).first()
            if item:
                if return_qty > item.quantity:
                    return jsonify({'success': False, 'message': f'Tirada aad celisay ({return_qty}) way ka badan tahay intii la iibsaday ({item.quantity})'})
                
                # Create return item record
                ret_item = PurchaseReturnItem(
                    purchase_return=purchase_return,
                    product_id=item.product_id,
                    quantity=return_qty,
                    unit_cost=item.unit_cost
                )
                db.session.add(ret_item)
                
                # Update total amount on return header
                purchase_return.total_amount = return_qty * item.unit_cost
                
                # Deduct from original Purchase total
                return_amount = return_qty * item.unit_cost
                purchase.total_amount -= return_amount
                
                # Reduce from stock
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity -= return_qty
            else:
                return jsonify({'success': False, 'message': 'Alaabta lama helin!'})
        else:
            # Fallback: Original logic (if no specific product selected)
            purchase_items = PurchaseItem.query.filter_by(purchase_id=purchase.id).all()
            total_ret_amount = 0
            for item in purchase_items:
                ret_item = PurchaseReturnItem(
                    purchase_return=purchase_return,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_cost=item.unit_cost
                )
                db.session.add(ret_item)
                total_ret_amount += item.quantity * item.unit_cost
                
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity -= item.quantity
            
            purchase.total_amount -= total_ret_amount
            purchase_return.total_amount = total_ret_amount
            
        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_return(purchase_return, type='PURCHASE')
        
        # IMPORTANT: Commit all changes including purchase.total_amount adjustment
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alaabta waa la celiyay, deyntiina waa laga jaray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/cash-by-ap')
@login_required
def cash_by_ap():
    # Shows vendor balances (Accounts Payable)
    vendors_list = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    ap_data = []
    for v in vendors_list:
        total_purchases = db.session.query(db.func.sum(Purchase.total_amount)).filter(
            Purchase.vendor_id == v.id,
            db.func.lower(Purchase.payment_method).in_(['credit', 'ap'])
        ).scalar() or 0
        total_paid = db.session.query(db.func.sum(VendorPayment.amount)).filter_by(vendor_id=v.id).scalar() or 0
        balance = total_purchases - total_paid
        if balance > 0:
            ap_data.append({
                'vendor': v,
                'total_purchases': total_purchases,
                'total_paid': total_paid,
                'balance': balance
            })
    return render_template('vendor/cash_by_ap.html', ap_data=ap_data)

@vendor.route('/vendor/paid', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def paid():
    if request.method == 'POST':
        vendor_id = request.form.get('vendor_id')
        amount = request.form.get('amount')
        method = request.form.get('payment_method')
        ref = request.form.get('reference_no')
        amount_val = float(amount)
        from app.services.accounting_service import AccountingService
        account = AccountingService.get_account(method, current_user.tenant_id)
        if account:
            balance = AccountingService.get_account_balance(account.id, current_user.tenant_id)
            if balance < amount_val:
                flash(f'Cilad! Akoonka {account.account_name} kuguma filna. Haraagu waa ${balance:,.2f}', 'danger')
                return redirect(url_for('vendor.paid'))
                
        new_payment = VendorPayment(
            vendor_id=vendor_id,
            amount=float(amount),
            payment_method=method,
            reference_no=ref,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_payment)
        db.session.flush()

        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_vendor_payment(new_payment)

        db.session.commit()
        flash('Lacag bixinta waa la kaydiyay!', 'success')
        return redirect(url_for('vendor.paid'))
        
    all_payments = VendorPayment.query.filter_by(tenant_id=current_user.tenant_id).order_by(VendorPayment.created_at.desc()).all()
    vendors_list = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Load bank accounts from Chart of Accounts
    bank_accounts = ChartAccount.query.filter(
        ChartAccount.tenant_id == current_user.tenant_id,
        ChartAccount.category == 'ASSETS',
        ChartAccount.sub_category.in_(['Bank', 'Cash', 'Bank Accounts'])
    ).all()
    if not bank_accounts:
        bank_accounts = BankAccount.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('vendor/paid.html', payments=all_payments, vendors=vendors_list, bank_accounts=bank_accounts)

@vendor.route('/vendor/edit/<int:id>', methods=['POST'])
@login_required
def edit_vendor(id):
    v = Vendor.query.get_or_404(id)
    if v.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        v.name = data['name']
        v.phone = data.get('phone')
        v.email = data.get('email')
        v.address = data.get('address')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_vendor(id):
    v = Vendor.query.get_or_404(id)
    if v.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Check if vendor has purchases
        if v.purchases:
            return jsonify({'success': False, 'message': 'Ma tiri kartid vendor-kan maxaa yeelay iib hore ayuu leeyahay!'})
        db.session.delete(v)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@vendor.route('/vendor/returns', methods=['GET', 'POST'])
@login_required
def returns():
    from app.models import PurchaseReturn, Purchase, Vendor, Branch, Product
    if request.method == 'POST':
        # Logic for standalone add return (if needed)
        pass
        
    returns_list = PurchaseReturn.query.filter_by(tenant_id=current_user.tenant_id).order_by(PurchaseReturn.created_at.desc()).all()
    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    branches = Branch.query.filter_by(tenant_id=current_user.tenant_id).all()
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return render_template('vendor/returns.html', 
                           returns=returns_list, 
                           vendors=vendors, 
                           branches=branches, 
                           products=products)

@vendor.route('/vendor/returns/add', methods=['POST'])
@login_required
def add_purchase_return():
    from app.models import PurchaseReturn, PurchaseReturnItem, Product, Purchase
    data = request.get_json()
    try:
        # Create a proxy purchase record since PurchaseReturn requires a purchase_id
        proxy_purchase = Purchase(
            invoice_no=data.get('invoice_no', 'RET-DUMMY'),
            vendor_id=data.get('vendor_id'),
            total_amount=0,
            payment_method='Cash',
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(proxy_purchase)
        db.session.flush()

        new_return = PurchaseReturn(
            purchase_id=proxy_purchase.id,
            invoice_no=data.get('invoice_no'),
            reason=f"Standalone Return (Vendor: {data.get('vendor_id')})",
            total_amount=sum(float(i['unit_cost']) * float(i['qty']) for i in data.get('items', [])),
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_return)
        db.session.flush()

        for item in data.get('items', []):
            ret_item = PurchaseReturnItem(
                purchase_return_id=new_return.id,
                product_id=item['product_id'],
                quantity=item['qty'],
                unit_cost=item['unit_cost']
            )
            db.session.add(ret_item)
            
            # Reduce from stock
            product = Product.query.get(item['product_id'])
            if product:
                product.stock_quantity -= float(item['qty'])

        # Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_return(new_return, type='PURCHASE')

        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase return added successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/payment/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_payment(id):
    payment = VendorPayment.query.get_or_404(id)
    if payment.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(f"VPMT-{payment.id}", current_user.tenant_id)
        
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Lacag bixinta waa la tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
