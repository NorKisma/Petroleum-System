from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Customer
from app.utils.module_access import module_required

customers = Blueprint('customers', __name__)

@customers.route('/customers')
@login_required
@module_required('contacts')
def list_customers():
    all_customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('customers/index.html', customers=all_customers)

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
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la kaydiyay!'})
    except Exception as e:
        db.session.rollback()
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
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la bedelay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@customers.route('/customers/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    if customer.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Fadlan iska hubi.'})
    
    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macmiilka waa la tiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
