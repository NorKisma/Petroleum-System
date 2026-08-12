from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Vendor
from app import db
from app.utils.decorators import roles_required

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
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

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
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@vendor.route('/vendor/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_vendor(id):
    v = Vendor.query.get_or_404(id)
    if v.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendor deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
