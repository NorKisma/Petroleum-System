from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Customer, Sale, CustomerPayment, CustomerGroup
from datetime import datetime

customers = Blueprint('customers', __name__)

@customers.route('/customers')
@login_required
def list_customers():
    all_customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    all_groups = CustomerGroup.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('customers/index.html', customers=all_customers, groups=all_groups)

@customers.route('/customers/sales-cash')
@login_required
def sales_cash():
    from app.models import Product, ChartAccount
    sales = Sale.query.filter_by(tenant_id=current_user.tenant_id, payment_method='Cash').order_by(Sale.created_at.desc()).all()
    customers_list = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    products_list = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Fetch liquid asset accounts
    bank_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS').all()
    
    return render_template('customers/sales_cash.html', 
                           sales=sales, 
                           customers=customers_list, 
                           products=products_list,
                           accounts=bank_accounts,
                           now_date=datetime.utcnow().strftime('%Y-%m-%d'))

@customers.route('/customers/sales-cash/add', methods=['POST'])
@login_required
def add_sale_cash():
    from app.models import Product, SaleItem
    import uuid
    data = request.get_json()
    try:
        items = data.get('items', [])
        if not items:
            return jsonify({'success': False, 'message': 'No items added'})

        subtotal = sum(float(i['qty']) * float(i['price']) for i in items)
        vat_rate = float(data.get('vat_rate') or 0)
        discount = float(data.get('discount_amount') or 0)
        
        total_amount = subtotal + (subtotal * vat_rate / 100) - discount
        
        # Create Sale
        new_sale = Sale(
            invoice_no=str(uuid.uuid4())[:8].upper(),
            subtotal=subtotal,
            tax_amount=(subtotal * vat_rate / 100),
            discount_amount=discount,
            total_amount=total_amount,
            payment_method=data.get('payment_method', 'Cash'),
            customer_id=data.get('customer_id') if data.get('customer_id') else None,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            attachment=data.get('attachment'),
            created_at=datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else datetime.utcnow()
        )
        db.session.add(new_sale)
        db.session.flush() # Get ID

        # Process Items
        for i in items:
            product = Product.query.get(i['product_id'])
            if product:
                # Update Stock
                product.stock_quantity -= int(i['qty'])
                
                # Create Sale Item
                sale_item = SaleItem(
                    sale_id=new_sale.id,
                    product_id=product.id,
                    quantity=int(i['qty']),
                    buy_price=product.buy_price, # Store buy price at time of sale for profit calculation
                    unit_price=float(i['price']),
                    size=i.get('size')
                )
                db.session.add(sale_item)

        db.session.commit()

        # Professional Accounting Integration for Sale
        from app.services.accounting_service import AccountingService
        AccountingService.record_sale(new_sale)
        db.session.commit()

        # 3. Record Payment (if any lacag was paid)
        from app.models import BankAccount, CustomerPayment
        account_id = data.get('account_id')
        paid_amount = float(data.get('paid_amount') or 0)
        
        if account_id and paid_amount > 0:
            account = BankAccount.query.get(account_id)
            if account:
                payment = CustomerPayment(
                    customer_id=new_sale.customer_id, # Can be None for walk-in
                    amount=paid_amount,
                    payment_method=account.account_code if hasattr(account, 'account_code') else account.account_name,
                    reference_no=f"SALE-{new_sale.invoice_no}",
                    tenant_id=current_user.tenant_id,
                    payment_date=new_sale.created_at
                )
                db.session.add(payment)
                db.session.flush()

                # Professional Accounting Integration for Payment
                from app.services.accounting_service import AccountingService
                AccountingService.record_customer_payment(payment)
                db.session.commit()

        return jsonify({'success': True, 'message': 'Sale recorded successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/invoices')
@login_required
def invoices():
    invoices = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all()
    customers_list = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('customers/invoices.html', invoices=invoices, customers=customers_list)

@customers.route('/customers/sale/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_sale(id):
    from app.models import Sale, SaleItem, Product
    sale = Sale.query.get_or_404(id)
    if sale.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Reverse inventory changes
        items = SaleItem.query.filter_by(sale_id=sale.id).all()
        for item in items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity
        
        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(sale.invoice_no, current_user.tenant_id)
        
        db.session.delete(sale)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Sale deleted and inventory adjusted!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/sale/return/<int:id>', methods=['POST'])
@login_required
def return_sale(id):
    from app.models import Sale, SaleItem, SaleReturn, SaleReturnItem, Product
    sale = Sale.query.get_or_404(id)
    if sale.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    product_name = data.get('product')
    return_qty = int(data.get('qty', 0))
    reason = data.get('reason', 'Client Return')
    
    try:
        # Create Sale Return Header if it doesn't exist for this invoice, or append to it
        # To keep it simple, we'll create a new one per return action
        sale_return = SaleReturn(
            sale_id=sale.id,
            invoice_no=sale.invoice_no,
            total_amount=0, # Will update below
            reason=reason,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(sale_return)
        
        # Find the specific item in the sale
        sale_item = None
        for item in sale.items:
            if item.product.name == product_name:
                sale_item = item
                break
        
        if sale_item:
            if return_qty > sale_item.quantity:
                return jsonify({'success': False, 'message': 'Tirada la celinayo way ka badan tahay intii la iibiyay!'})
                
            ret_item = SaleReturnItem(
                sale_return=sale_return,
                product_id=sale_item.product_id,
                quantity=return_qty,
                unit_price=sale_item.unit_price
            )
            db.session.add(ret_item)
            sale_return.total_amount = return_qty * sale_item.unit_price
            
            # Add back to stock
            product = Product.query.get(sale_item.product_id)
            if product:
                product.stock_quantity += return_qty
            
            # Deduct from original Sale total
            return_amount = return_qty * sale_item.unit_price
            sale.total_amount -= return_amount
            
            # Professional Accounting Integration
            from app.services.accounting_service import AccountingService
            AccountingService.record_return(sale_return, type='SALE')
            
        else:
            return jsonify({'success': False, 'message': 'Alaabta lama helin iibkan dhexdiisa!'})
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alaabta waa la celiyay, lacagtiina waa la jarmay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/cash-to-ar')
@login_required
def cash_to_ar():
    # This view shows customer balances (Accounts Receivable)
    customers_list = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ar_data = []
    for c in customers_list:
        total_sales = db.session.query(db.func.sum(Sale.total_amount)).filter_by(customer_id=c.id).scalar() or 0
        total_payments = db.session.query(db.func.sum(CustomerPayment.amount)).filter_by(customer_id=c.id).scalar() or 0
        balance = total_sales - total_payments
        if balance > 0:
            ar_data.append({
                'customer': c,
                'total_sales': total_sales,
                'total_payments': total_payments,
                'balance': balance
            })
    return render_template('customers/cash_to_ar.html', ar_data=ar_data)

@customers.route('/customers/receipts', methods=['GET', 'POST'])
@login_required
def receipts():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        amount = request.form.get('amount')
        method = request.form.get('payment_method')
        ref = request.form.get('reference_no')
        
        new_payment = CustomerPayment(
            customer_id=customer_id,
            amount=float(amount),
            payment_method=method,
            reference_no=ref,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_payment)
        db.session.flush()

        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_customer_payment(new_payment)

        db.session.commit()
        flash('Lacag qabashada waa la kaydiyay!', 'success')
        return redirect(url_for('customers.receipts'))
        
    all_receipts = CustomerPayment.query.filter_by(tenant_id=current_user.tenant_id).order_by(CustomerPayment.created_at.desc()).all()
    customers_list = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('customers/receipts.html', receipts=all_receipts, customers=customers_list)

@customers.route('/customers/receipt/edit/<int:id>', methods=['POST'])
@login_required
def edit_receipt(id):
    receipt = CustomerPayment.query.get_or_404(id)
    if receipt.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        from app.services.accounting_service import AccountingService
        
        # Remove old accounting entries
        AccountingService.delete_entries(f"RCPT-{receipt.id}", current_user.tenant_id)
        
        # Update receipt
        receipt.customer_id = data.get('customer_id')
        receipt.amount = float(data.get('amount'))
        receipt.payment_method = data.get('payment_method')
        receipt.reference_no = data.get('reference_no')
        db.session.commit()
        
        # Add new accounting entries
        AccountingService.record_customer_payment(receipt)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Receipt updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/receipt/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_receipt(id):
    receipt = CustomerPayment.query.get_or_404(id)
    if receipt.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.services.accounting_service import AccountingService
        
        # Remove accounting entries
        AccountingService.delete_entries(f"RCPT-{receipt.id}", current_user.tenant_id)
        
        db.session.delete(receipt)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receipt deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/add', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json()
    try:
        new_customer = Customer(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            customer_group_id=int(data.get('customer_group_id')) if data.get('customer_group_id') else None,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la kaydiyay!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/edit/<int:id>', methods=['POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if customer.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    data = request.get_json()
    try:
        customer.name = data['name']
        customer.phone = data.get('phone')
        customer.email = data.get('email')
        customer.address = data.get('address')
        customer.customer_group_id = int(data.get('customer_group_id')) if data.get('customer_group_id') else None
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la bedelay!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    if customer.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    try:
        if customer.sales:
            return jsonify({'success': False, 'message': 'Ma tiri kartid macmiilkan maxaa yeelay iib hore ayuu leeyahay!'})
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la tiray!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/groups')
@login_required
def list_customer_groups():
    groups = CustomerGroup.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('customers/groups.html', groups=groups)

@customers.route('/customers/groups/add', methods=['POST'])
@login_required
def add_customer_group():
    data = request.get_json()
    try:
        new_group = CustomerGroup(
            name=data['name'],
            calculation_percentage=float(data.get('calculation_percentage', 0.0)),
            selling_price_group=data.get('selling_price_group', ''),
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_group)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kooxda Macmiilka waa la kaydiyay!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/groups/edit/<int:id>', methods=['POST'])
@login_required
def edit_customer_group(id):
    group = CustomerGroup.query.get_or_404(id)
    if group.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    data = request.get_json()
    try:
        group.name = data['name']
        group.calculation_percentage = float(data.get('calculation_percentage', 0.0))
        group.selling_price_group = data.get('selling_price_group', '')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kooxda Macmiilka waa la bedelay!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/groups/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_customer_group(id):
    group = CustomerGroup.query.get_or_404(id)
    if group.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    try:
        if group.customers:
            return jsonify({'success': False, 'message': 'Ma tiri kartid kooxdan maxaa yeelay macaamiil ayaa ku xiran!'})
        db.session.delete(group)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kooxda Macmiilka waa la tiray!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
