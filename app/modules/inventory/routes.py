from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Unit, Brand, StockTransfer, StockTransferItem, Branch
from app.services.email_service import EmailService
from app.utils.decorators import roles_required
from app.utils.audit import log_audit
from app.services.reporting_service import ReportingService
from datetime import datetime

inventory = Blueprint('inventory', __name__)

@inventory.route('/inventory/transfers')
@login_required
def list_transfers():
    transfers = StockTransfer.query.filter_by(tenant_id=current_user.tenant_id).order_by(StockTransfer.created_at.desc()).all()
    return render_template('inventory/transfers.html', transfers=transfers)

@inventory.route('/inventory/transfer/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def add_transfer():
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_transfer = StockTransfer(
                reference_no=data.get('reference_no', f"TR-{datetime.utcnow().timestamp()}"),
                from_branch_id=data['from_branch_id'],
                to_branch_id=data['to_branch_id'],
                shipping_charges=float(data.get('shipping_charges', 0)),
                additional_notes=data.get('additional_notes'),
                user_id=current_user.id,
                tenant_id=current_user.tenant_id
            )
            db.session.add(new_transfer)
            db.session.flush()

            for item in data['items']:
                t_item = StockTransferItem(
                    transfer_id=new_transfer.id,
                    product_id=item['product_id'],
                    quantity=int(item['quantity']),
                    unit_price=float(item.get('unit_price', 0))
                )
                db.session.add(t_item)
                
                # Update Stock
                product = Product.query.get(item['product_id'])
                if product:
                    product.stock_quantity -= int(item['quantity'])
            
            db.session.commit()
            log_audit('STOCK_TRANSFER', 'INVENTORY', f'Transferred stock: {new_transfer.reference_no}')
            return jsonify({'success': True, 'message': 'Wareejinta waa lagu guulaystay!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

    branches = Branch.query.filter_by(tenant_id=current_user.tenant_id).all()
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('inventory/add_transfer.html', branches=branches, products=products)

@inventory.route('/inventory/next-barcode')
@login_required
def next_barcode():
    last_product = Product.query.filter_by(tenant_id=current_user.tenant_id).order_by(Product.id.desc()).first()
    if last_product and last_product.id:
        next_val = 1000 + last_product.id + 1
    else:
        next_val = 1001
    return jsonify({'next_barcode': str(next_val)})

@inventory.route('/inventory')
@login_required
def list_products():
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('inventory/index.html', products=products, categories=categories)

@inventory.route('/inventory/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def add_product():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        try:
            new_product = Product(
                name=data['name'],
                barcode=data.get('barcode') if data.get('barcode') else None,
                description=data.get('description'),
                buy_price=float(data['buy_price']),
                sell_price=float(data['sell_price']),
                stock_quantity=int(data['stock_quantity']),
                low_stock_threshold=float(data.get('low_stock_threshold', 10.0)),
                is_active=bool(int(data.get('is_active', 1))),
                category_id=int(data['category_id']) if data.get('category_id') else None,
                unit_id=int(data['unit_id']) if data.get('unit_id') else None,
                brand_id=int(data['brand_id']) if data.get('brand_id') else None,
                tenant_id=current_user.tenant_id
            )
            db.session.add(new_product)
            db.session.commit()
            
            log_audit('ADD_PRODUCT', 'INVENTORY', f'Added product: {new_product.name}')
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Alaabta waa la kaydiyay!'})
            else:
                flash('Alaabta waa la kaydiyay!', 'success')
                return redirect(url_for('inventory.list_products'))
        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'message': str(e)})
            else:
                flash(str(e), 'danger')
                return redirect(url_for('inventory.add_product'))
    
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    units = Unit.query.filter_by(tenant_id=current_user.tenant_id).all()
    brands = Brand.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('inventory/add_product.html', categories=categories, units=units, brands=brands)

@inventory.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.tenant_id != current_user.tenant_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
        flash('Access denied', 'danger')
        return redirect(url_for('inventory.list_products'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        try:
            product.name = data['name']
            product.barcode = data.get('barcode', product.barcode)
            product.description = data.get('description', product.description)
            product.buy_price = float(data['buy_price'])
            product.sell_price = float(data['sell_price'])
            product.stock_quantity = int(data['stock_quantity'])
            product.low_stock_threshold = float(data.get('low_stock_threshold', product.low_stock_threshold))
            
            if 'is_active' in data:
                product.is_active = bool(int(data['is_active']))
                
            product.category_id = int(data['category_id']) if data.get('category_id') else None
            product.unit_id = int(data['unit_id']) if data.get('unit_id') else None
            product.brand_id = int(data['brand_id']) if data.get('brand_id') else None
                
            db.session.commit()
            
            log_audit('EDIT_PRODUCT', 'INVENTORY', f'Updated product: {product.name}')
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Alaabta waa la bedelay!'})
            else:
                flash('Alaabta waa la bedelay!', 'success')
                return redirect(url_for('inventory.list_products'))
        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'message': str(e)})
            else:
                flash(str(e), 'danger')
                return redirect(url_for('inventory.edit_product', id=id))
    
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    units = Unit.query.filter_by(tenant_id=current_user.tenant_id).all()
    brands = Brand.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('inventory/edit_product.html', product=product, categories=categories, units=units, brands=brands)

@inventory.route('/inventory/unit/add', methods=['POST'])
@login_required
def add_unit():
    data = request.get_json()
    name = data.get('name')
    if name:
        new_unit = Unit(name=name, tenant_id=current_user.tenant_id)
        db.session.add(new_unit)
        db.session.commit()
        return jsonify({'success': True, 'id': new_unit.id, 'name': new_unit.name})
    return jsonify({'success': False, 'message': 'Name is required'})

@inventory.route('/inventory/brand/add', methods=['POST'])
@login_required
def add_brand():
    data = request.get_json()
    name = data.get('name')
    if name:
        new_brand = Brand(name=name, tenant_id=current_user.tenant_id)
        db.session.add(new_brand)
        db.session.commit()
        return jsonify({'success': True, 'id': new_brand.id, 'name': new_brand.name})
    return jsonify({'success': False, 'message': 'Name is required'})

@inventory.route('/inventory/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
@roles_required('admin', 'manager', 'developer')
def delete_product(id):
    product = Product.query.get_or_404(id)
    if product.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    try:
        from app.models import SaleItem, PurchaseItem
        has_sales = SaleItem.query.filter_by(product_id=id).first()
        has_purchases = PurchaseItem.query.filter_by(product_id=id).first()
        
        if has_sales or has_purchases:
            return jsonify({'success': False, 'message': 'Alaabtaaan lama tiri karo waayo taariikh ayay leedahay. Fadlan Deactivate dheh.'})
            
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        log_audit('DELETE_PRODUCT', 'INVENTORY', f'Deleted product: {product_name}')
        return jsonify({'success': True, 'message': 'Alaabta waa la tiray!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@inventory.route('/inventory/categories', methods=['GET', 'POST'])
@login_required
def list_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_cat = Category(name=name, tenant_id=current_user.tenant_id)
            db.session.add(new_cat)
            db.session.commit()
            flash('Category added!', 'success')
        return redirect(url_for('inventory.list_categories'))
    categories = Category.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('inventory/categories.html', categories=categories)

@inventory.route('/inventory/category/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def edit_category(id):
    category = Category.query.get_or_404(id)
    if category.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'})
    data = request.get_json()
    category.name = data['name']
    db.session.commit()
    log_audit('EDIT_CATEGORY', 'INVENTORY', f'Updated category: {category.name}')
    return jsonify({'success': True})

@inventory.route('/inventory/category/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'manager', 'developer')
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'})
    has_products = Product.query.filter_by(category_id=id).first()
    if has_products:
        return jsonify({'success': False, 'message': 'Qaybtaan lama tirtiri karo waayo alaab ayaa ku jirta.'})
    db.session.delete(category)
    db.session.commit()
    log_audit('DELETE_CATEGORY', 'INVENTORY', f'Deleted category: {category.name}')
    return jsonify({'success': True})

@inventory.route('/inventory/stock-adjustment', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def stock_adjustment():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        new_qty = request.form.get('new_quantity')
        reason = request.form.get('reason')
        product = Product.query.get_or_404(product_id)
        if product.tenant_id == current_user.tenant_id:
            old_qty = product.stock_quantity
            product.stock_quantity = int(new_qty)
            from app.models import AuditLog
            log = AuditLog(user_id=current_user.id, action=f"Stock Adjustment: {product.name}",
                          description=f"Changed from {old_qty} to {new_qty}. Reason: {reason}",
                          tenant_id=current_user.tenant_id)
            db.session.add(log)
            db.session.commit()
            flash('Stock adjusted successfully!', 'success')
        return redirect(url_for('inventory.stock_adjustment'))
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    from app.models import AuditLog
    recent_logs = AuditLog.query.filter_by(tenant_id=current_user.tenant_id)\
        .filter(AuditLog.action.like('Stock Adjustment%'))\
        .order_by(AuditLog.created_at.desc()).limit(10).all()
    return render_template('inventory/stock_adjustment.html', products=products, logs=recent_logs)

@inventory.route('/inventory/report')
@login_required
def inventory_report():
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    total_products = len(products)
    total_cost = sum((p.buy_price or 0) * (p.stock_quantity or 0) for p in products)
    total_sales = sum((p.sell_price or 0) * (p.stock_quantity or 0) for p in products)
    total_profit = total_sales - total_cost
    return render_template('inventory/report.html', products=products, total_products=total_products,
                           total_cost=total_cost, total_sales=total_sales, total_profit=total_profit)

@inventory.route('/inventory/import-opening-stock', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'manager', 'developer')
def import_opening_stock():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash('Fadlan soo geli fayl CSV ah oo sax ah!', 'danger')
            return redirect(url_for('inventory.import_opening_stock'))
            
        import csv
        import io
        from app.models import AuditLog
        
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.reader(stream)
            
            # Skip header row
            header = next(csv_reader, None)
            
            success_count = 0
            errors = []
            row_idx = 1
            
            for row in csv_reader:
                row_idx += 1
                if not row or len(row) < 4:
                    continue
                    
                sku = row[0].strip()
                location = row[1].strip() if len(row) > 1 else ''
                qty_str = row[2].strip()
                cost_str = row[3].strip()
                
                if not sku:
                    errors.append(f"Row {row_idx}: SKU waa maran yahay.")
                    continue
                    
                # Validate product existence
                product = Product.query.filter_by(barcode=sku, tenant_id=current_user.tenant_id).first()
                if not product:
                    errors.append(f"Row {row_idx}: Alaab wadata SKU-ga '{sku}' lagama helin nidaamka.")
                    continue
                    
                # Validate quantity
                try:
                    qty = int(qty_str)
                except ValueError:
                    errors.append(f"Row {row_idx} ({sku}): Tirada '{qty_str}' ma ahan tiro sax ah.")
                    continue
                    
                # Validate cost
                try:
                    cost = float(cost_str)
                except ValueError:
                    errors.append(f"Row {row_idx} ({sku}): Qiimaha '{cost_str}' ma ahan qiimo sax ah.")
                    continue
                    
                # Update product
                old_qty = product.stock_quantity
                product.stock_quantity = qty
                product.buy_price = cost
                success_count += 1
                
                # Log audit per product
                log_desc = f"Imported Opening Stock for SKU {sku}. Changed qty from {old_qty} to {qty}, cost to {cost}."
                audit = AuditLog(
                    user_id=current_user.id,
                    action=f"Import Opening Stock: {product.name}",
                    description=log_desc,
                    tenant_id=current_user.tenant_id
                )
                db.session.add(audit)
                
            db.session.commit()
            
            if success_count > 0:
                flash(f"Si guul ah ayaa loo cusboonaysiiyay {success_count} alaabood!", "success")
            if errors:
                for err in errors[:10]: # limit flash messages
                    flash(err, "warning")
                if len(errors) > 10:
                    flash(f"...iyo {len(errors) - 10} khaladaad oo kale.", "warning")
                    
        except Exception as e:
            db.session.rollback()
            flash(f"Cillad ayaa dhacday inta lagu guda jiray soo dejinta: {str(e)}", "danger")
            
        return redirect(url_for('inventory.import_opening_stock'))
        
    return render_template('inventory/import_opening_stock.html')

@inventory.route('/inventory/import-opening-stock/template')
@login_required
def download_opening_stock_template():
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['SKU', 'Location', 'Quantity', 'Unit Cost (Before Tax)', 'Lot / batch number', 'Expiry Date'])
    writer.writerow(['1001', 'Main Branch', '100', '15.50', 'LOT-001', '18/05/2026'])
    writer.writerow(['1002', 'Main Branch', '50', '25.00', '', ''])
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=opening_stock_template.csv"
    return response
