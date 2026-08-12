from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Shareholder, ShareInvestment, ShareWithdrawal, ChartAccount
from app import db
from app.utils.decorators import roles_required
from datetime import datetime

share = Blueprint('share', __name__)

@share.route('/share/register')
@login_required
def register():
    shareholders = Shareholder.query.filter_by(tenant_id=current_user.tenant_id).all()
    # Annotate with totals
    share_data = []
    for s in shareholders:
        total_inv = db.session.query(db.func.sum(ShareInvestment.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        total_with = db.session.query(db.func.sum(ShareWithdrawal.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        balance = total_inv - total_with
        share_data.append({
            'obj': s,
            'total_invested': total_inv,
            'total_withdrawn': total_with,
            'balance': balance
        })
    return render_template('share/index.html', shareholders=share_data)

@share.route('/share/add-shareholder', methods=['POST'])
@login_required
def add_shareholder():
    data = request.get_json()
    try:
        new_s = Shareholder(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_s)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Shareholder registered!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@share.route('/share/shareholder/edit/<int:id>', methods=['POST'])
@login_required
def edit_shareholder(id):
    s = Shareholder.query.get_or_404(id)
    if s.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        s.name = data['name']
        s.phone = data.get('phone')
        s.email = data.get('email')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xogta waa la cusbooneysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@share.route('/share/shareholder/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_shareholder(id):
    s = Shareholder.query.get_or_404(id)
    if s.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        db.session.delete(s)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Saamilayda waa la tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@share.route('/share/investment', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def investment():
    if request.method == 'POST':
        s_id = request.form.get('shareholder_id')
        amount = request.form.get('amount')
        desc = request.form.get('description')
        account_id = request.form.get('account_id')
        
        new_inv = ShareInvestment(
            shareholder_id=s_id,
            amount=float(amount),
            description=desc,
            account_id=account_id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_inv)
        db.session.flush()
        
        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_share_investment(new_inv)
        
        db.session.commit()
        
        flash('Investment recorded!', 'success')
        return redirect(url_for('share.investment'))
        
    investments = ShareInvestment.query.filter_by(tenant_id=current_user.tenant_id).order_by(ShareInvestment.investment_date.desc()).all()
    shareholders = Shareholder.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    # Fetch liquid accounts (Bank/Cash)
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    bank_accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    return render_template('share/investment.html', investments=investments, shareholders=shareholders, bank_accounts=bank_accounts)

@share.route('/share/withdrawal', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def withdrawal():
    if request.method == 'POST':
        s_id = request.form.get('shareholder_id')
        amount = request.form.get('amount')
        desc = request.form.get('description')
        account_id = request.form.get('account_id')
        
        new_with = ShareWithdrawal(
            shareholder_id=s_id,
            amount=float(amount),
            description=desc,
            account_id=account_id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_with)
        db.session.flush()
        
        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_share_withdrawal(new_with)
        
        db.session.commit()
        
        flash('Withdrawal recorded!', 'success')
        return redirect(url_for('share.withdrawal'))
        
    withdrawals = ShareWithdrawal.query.filter_by(tenant_id=current_user.tenant_id).order_by(ShareWithdrawal.withdrawal_date.desc()).all()
    shareholders = Shareholder.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    # Fetch liquid accounts (Bank/Cash)
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    bank_accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    return render_template('share/withdrawal.html', withdrawals=withdrawals, shareholders=shareholders, bank_accounts=bank_accounts)

# Investment CRUD
@share.route('/share/investment/edit/<int:id>', methods=['POST'])
@login_required
def edit_investment(id):
    inv = ShareInvestment.query.get_or_404(id)
    if inv.tenant_id != current_user.tenant_id:
        flash('Access denied', 'danger')
        return redirect(url_for('share.investment'))
    
    inv.shareholder_id = request.form.get('shareholder_id')
    inv.amount = float(request.form.get('amount'))
    inv.description = request.form.get('description')
    inv.account_id = request.form.get('account_id')
    db.session.commit()
    flash('Investment updated!', 'success')
    return redirect(url_for('share.investment'))

@share.route('/share/investment/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_investment(id):
    inv = ShareInvestment.query.get_or_404(id)
    if inv.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    db.session.delete(inv)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Investment deleted!'})

# Withdrawal CRUD
@share.route('/share/withdrawal/edit/<int:id>', methods=['POST'])
@login_required
def edit_withdrawal(id):
    withd = ShareWithdrawal.query.get_or_404(id)
    if withd.tenant_id != current_user.tenant_id:
        flash('Access denied', 'danger')
        return redirect(url_for('share.withdrawal'))
    
    withd.shareholder_id = request.form.get('shareholder_id')
    withd.amount = float(request.form.get('amount'))
    withd.description = request.form.get('description')
    withd.account_id = request.form.get('account_id')
    db.session.commit()
    flash('Withdrawal updated!', 'success')
    return redirect(url_for('share.withdrawal'))

@share.route('/share/withdrawal/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_withdrawal(id):
    withd = ShareWithdrawal.query.get_or_404(id)
    if withd.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    db.session.delete(withd)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Withdrawal deleted!'})

@share.route('/share/statement')
@login_required
def statement():
    shareholders = Shareholder.query.filter_by(tenant_id=current_user.tenant_id).all()
    statements = []
    for s in shareholders:
        total_inv = db.session.query(db.func.sum(ShareInvestment.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        total_with = db.session.query(db.func.sum(ShareWithdrawal.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        statements.append({
            'shareholder': s,
            'total_invested': total_inv,
            'total_withdrawn': total_with,
            'balance': total_inv - total_with
        })
    return render_template('share/statement.html', statements=statements)
