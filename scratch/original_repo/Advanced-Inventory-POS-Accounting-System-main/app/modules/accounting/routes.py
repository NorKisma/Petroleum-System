from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Sale, SaleItem, Expense, OtherIncome, Asset, BankAccount, BankTransfer, Customer, Vendor, Purchase, CustomerPayment, VendorPayment, Product, Shareholder, ShareInvestment, ShareWithdrawal, ChartAccount, JournalEntry, JournalLine, SaleReturn, PurchaseReturn
from app.utils.reports import generate_sales_report, generate_expenses_report, generate_financial_report, generate_balance_sheet_report, generate_inventory_report, generate_cash_flow_report
from app.utils.decorators import roles_required
from app.services.reporting_service import ReportingService
from sqlalchemy import func
from datetime import datetime

accounting = Blueprint('accounting', __name__)

@accounting.route('/accounting/return/sale/add', methods=['POST'])
@login_required
def add_sale_return():
    from app.models import SaleReturn, SaleReturnItem, Product, Sale
    data = request.get_json()
    try:
        sale_id = data.get('sale_id')
        sale = Sale.query.get_or_404(sale_id)
        
        if sale.tenant_id != current_user.tenant_id:
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        new_return = SaleReturn(
            sale_id=sale.id,
            invoice_no=f"RET-{sale.invoice_no}",
            reason=data.get('reason', 'Damaged Product'),
            total_amount=sum(float(i['unit_price']) * float(i['qty']) for i in data.get('items', [])),
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_return)
        db.session.flush()

        for item in data.get('items', []):
            ret_item = SaleReturnItem(
                sale_return_id=new_return.id,
                product_id=item['product_id'],
                quantity=item['qty'],
                unit_price=item['unit_price']
            )
            db.session.add(ret_item)
            
            # Restock items
            product = Product.query.get(item['product_id'])
            if product:
                product.stock_quantity += float(item['qty'])

        # Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_return(new_return, type='SALE')

        # Reduce the original sale amount (to match your system's net-reporting style)
        sale.total_amount -= new_return.total_amount

        db.session.commit()
        return jsonify({'success': True, 'message': 'Sale return processed successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting')
@login_required
@roles_required('admin', 'accountant', 'developer', 'manager')
def dashboard():
    from app.services.accounting_service import AccountingService
    
    # Professional GL-based Summary
    summary = AccountingService.get_financial_summary(current_user.tenant_id)
    trends = AccountingService.get_monthly_trends(current_user.tenant_id)
    
    # Stock Valuation
    from app.models import Product
    all_products = Product.query.filter_by(tenant_id=current_user.tenant_id).all()
    stock_value = sum(p.stock_quantity * (p.buy_price or 0) for p in all_products)
    
    # Detailed Lists for UI
    expense_list = Expense.query.filter_by(tenant_id=current_user.tenant_id).order_by(Expense.created_at.desc()).limit(10).all()
    income_list = OtherIncome.query.filter_by(tenant_id=current_user.tenant_id).order_by(OtherIncome.created_at.desc()).limit(10).all()
    
    return render_template('accounting/index.html', 
                           revenue=summary['revenue'], 
                           cogs=summary['cogs'], 
                           expenses=summary['expenses'], 
                           gross_profit=summary['revenue'] - summary['cogs'], 
                           net_profit=summary['net_profit'],
                           stock_value=stock_value,
                           expense_list=expense_list,
                           income_list=income_list,
                           trends=trends)

@accounting.route('/accounting/budget', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def budget():
    from app.models import Sale, Expense, Purchase, OtherIncome
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    import calendar

    fiscal_year = request.args.get('year', datetime.now().year)
    try:
        fiscal_year = int(fiscal_year)
    except:
        fiscal_year = datetime.now().year

    if request.method == 'POST':
        flash('Budget saved successfully!', 'success')
        return redirect(url_for('accounting.budget', year=fiscal_year))

    # ── Historical averages (last 12 months) for AI suggestions ──────────────
    now = datetime.utcnow()
    twelve_months_ago = now - timedelta(days=365)

    avg_monthly_revenue = (
        db.session.query(func.sum(Sale.total_amount))
        .filter(Sale.tenant_id == current_user.tenant_id,
                Sale.created_at >= twelve_months_ago)
        .scalar() or 0
    ) / 12

    avg_monthly_cogs = (
        db.session.query(func.sum(Purchase.total_amount))
        .filter(Purchase.tenant_id == current_user.tenant_id,
                Purchase.created_at >= twelve_months_ago)
        .scalar() or 0
    ) / 12

    avg_monthly_expenses = (
        db.session.query(func.sum(Expense.amount))
        .filter(Expense.tenant_id == current_user.tenant_id,
                Expense.created_at >= twelve_months_ago)
        .scalar() or 0
    ) / 12

    avg_monthly_other_income = (
        db.session.query(func.sum(OtherIncome.amount))
        .filter(OtherIncome.tenant_id == current_user.tenant_id)
        .scalar() or 0
    ) / 12

    # ── AI Recommendations (rule-based smart budgeting) ────────────────────────
    growth_factor = 1.10  # 10% growth target

    ai_suggestions = {
        'Sales Revenue':       round(avg_monthly_revenue * growth_factor, 2),
        'Cost of Goods Sold':  round(avg_monthly_cogs * 1.05, 2),
        'Operating Expenses':  round(avg_monthly_expenses * 1.03, 2),
        'Other Income':        round(avg_monthly_other_income * growth_factor, 2),
        'Cash in Hand':        round(avg_monthly_revenue * 0.05, 2),
        'Bank Account':        round(avg_monthly_revenue * 0.20, 2),
        'Petty Cash':          round(avg_monthly_expenses * 0.08, 2),
        'Accounts Receivable': round(avg_monthly_revenue * 0.15, 2),
        'Inventory Asset':     round(avg_monthly_cogs * 1.15, 2),
        'Prepaid Expenses':    round(avg_monthly_expenses * 0.10, 2),
        'Fixed Assets':        round(avg_monthly_revenue * 0.03, 2),
        'Accumulated Depreciation': round(avg_monthly_revenue * 0.01, 2),
        'Accounts Payable':    round(avg_monthly_cogs * 0.30, 2),
        'Long Term Debt':      0,
        'Owner Equity':        0,
        'Retained Earnings':   round((avg_monthly_revenue - avg_monthly_cogs - avg_monthly_expenses) * 12, 2),
        'Tax Expense':         round((avg_monthly_revenue - avg_monthly_cogs - avg_monthly_expenses) * 0.20, 2),
        'Salaries & Wages':    round(avg_monthly_expenses * 0.40, 2),
        'Rent & Lease':        round(avg_monthly_expenses * 0.15, 2),
        'Utilities':           round(avg_monthly_expenses * 0.08, 2),
        'Office & Admin':      round(avg_monthly_expenses * 0.07, 2),
        'Bank Charges':        round(avg_monthly_expenses * 0.02, 2),
        'Depreciation':        round(avg_monthly_expenses * 0.03, 2),
        'Advertising & Marketing': round(avg_monthly_revenue * 0.04, 2),
        'Insurance':           round(avg_monthly_expenses * 0.03, 2),
        'Miscellaneous':       round(avg_monthly_expenses * 0.05, 2),
    }

    # ── Insight messages ───────────────────────────────────────────────────────
    insights = []
    net = avg_monthly_revenue - avg_monthly_cogs - avg_monthly_expenses
    margin = (net / avg_monthly_revenue * 100) if avg_monthly_revenue > 0 else 0

    if margin < 10:
        insights.append({'type': 'danger', 'icon': 'fa-exclamation-triangle',
            'msg': f'Net margin is only {margin:.1f}%. Consider cutting expenses by 5-10%.'})
    elif margin < 20:
        insights.append({'type': 'warning', 'icon': 'fa-info-circle',
            'msg': f'Net margin is {margin:.1f}%. Good, but there\'s room to grow.'})
    else:
        insights.append({'type': 'success', 'icon': 'fa-check-circle',
            'msg': f'Excellent! Net margin is {margin:.1f}%. Maintain this trajectory.'})

    if avg_monthly_cogs > avg_monthly_revenue * 0.6:
        insights.append({'type': 'warning', 'icon': 'fa-shopping-cart',
            'msg': 'COGS exceeds 60% of revenue. Negotiate better supplier rates.'})

    if avg_monthly_expenses > avg_monthly_revenue * 0.3:
        insights.append({'type': 'danger', 'icon': 'fa-receipt',
            'msg': 'Operating expenses are high (>30% of revenue). Review cost centers.'})

    accounts = [
        'Cash in Hand', 'Bank Account', 'Petty Cash', 'Accounts Receivable',
        'Inventory Asset', 'Prepaid Expenses', 'Fixed Assets',
        'Accumulated Depreciation', 'Accounts Payable', 'Long Term Debt',
        'Owner Equity', 'Retained Earnings', 'Sales Revenue', 'Other Income',
        'Cost of Goods Sold', 'Operating Expenses', 'Tax Expense',
        'Salaries & Wages', 'Rent & Lease', 'Utilities', 'Office & Admin',
        'Bank Charges', 'Depreciation', 'Advertising & Marketing',
        'Insurance', 'Miscellaneous'
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    quarters = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']
    years_available = list(range(datetime.now().year - 2, datetime.now().year + 4))

    return render_template('accounting/budget.html',
                           accounts=accounts, months=months, quarters=quarters,
                           fiscal_year=fiscal_year, years_available=years_available,
                           ai_suggestions=ai_suggestions, insights=insights,
                           avg_revenue=avg_monthly_revenue,
                           avg_expenses=avg_monthly_expenses,
                           avg_cogs=avg_monthly_cogs)

@accounting.route('/accounting/expenses', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def expenses():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category')
        amount_val = float(amount)
        payment_account = request.form.get('payment_account')
        
        # Check if account has sufficient balance
        from app.services.accounting_service import AccountingService
        account = AccountingService.get_account(payment_account, current_user.tenant_id)
        if account:
            balance = AccountingService.get_account_balance(account.id, current_user.tenant_id)
            if balance < amount_val:
                flash(f'Cilad! Akoonka {account.account_name} kuguma filna. Haraagu waa ${balance:,.2f}', 'danger')
                return redirect(url_for('accounting.expenses'))
                
        new_expense = Expense(
            description=description,
            amount=float(amount),
            category=category, 
            payment_account=request.form.get('payment_account'),
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_expense)
        db.session.flush() # Get ID

        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_expense(new_expense)

        db.session.commit()
        flash('Kharashka waa la kaydiyay!', 'success')
        return redirect(url_for('accounting.expenses'))
        
    from app.models import User, ChartAccount
    all_expenses = Expense.query.filter_by(tenant_id=current_user.tenant_id).order_by(Expense.created_at.desc()).all()
    staff = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    # Professional Dynamic Categories
    expense_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='EXPENSES', is_active=True).all()
    
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    bank_accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    return render_template('accounting/expenses.html', 
                           expenses=all_expenses, 
                           staff=staff, 
                           expense_accounts=expense_accounts, 
                           bank_accounts=bank_accounts)

@accounting.route('/accounting/expense/edit/<int:id>', methods=['POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        expense.description = data.get('description')
        expense.amount = float(data.get('amount'))
        expense.category = data.get('category')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Expense updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/expense/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Professional Accounting: Clean up journal entries
        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(f"EXP-{expense.id}", current_user.tenant_id)
        
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Expense deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/balance-sheet')
@login_required
def balance_sheet():
    from app.services.accounting_service import AccountingService
    from app.models import ChartAccount, Customer, Vendor, Shareholder, Sale, Purchase, CustomerPayment, VendorPayment, ShareInvestment, ShareWithdrawal
    from sqlalchemy import func

    # 1. Assets
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    bank_data = []
    total_bank_balance = 0
    inventory_value = 0
    other_assets_value = 0
    
    for acc in all_assets:
        balance = AccountingService.get_account_balance(acc.id, current_user.tenant_id)
        
        # Check specific account types FIRST to prevent them from falling into generic "Current Assets"
        if acc.account_code == '1100' or acc.sub_category in ['Accounts Receivable', 'Receivables']:
            pass  # handled below via direct query
        elif acc.account_code in ('1200', '1002') or acc.sub_category == 'Inventory':
            inventory_value += balance
        elif acc.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets'] or 'Cash' in acc.account_name or 'Bank' in acc.account_name:
            bank_data.append({'obj': acc, 'balance': balance})
            total_bank_balance += balance
        else:
            other_assets_value += balance

    # AR — direct from Sale/CustomerPayment (Returns are already subtracted from Sale.total_amount in DB)
    from app.models import Sale as SaleModel, CustomerPayment as CustPay
    _credit_sales = db.session.query(func.sum(SaleModel.total_amount))\
        .filter(SaleModel.tenant_id == current_user.tenant_id, SaleModel.payment_method.ilike('Credit')).scalar() or 0
    _cust_paid = db.session.query(func.sum(CustPay.amount))\
        .filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    receivables = max(_credit_sales - _cust_paid, 0)

    total_assets = total_bank_balance + receivables + inventory_value + other_assets_value
    
    # 2. Liabilities — AP direct from Purchase/VendorPayment (Returns are already subtracted from Purchase.total_amount in DB)
    from app.models import Purchase as PurchaseModel, VendorPayment as VendPay
    _credit_purchases = db.session.query(func.sum(PurchaseModel.total_amount))\
        .filter(PurchaseModel.tenant_id == current_user.tenant_id, PurchaseModel.payment_method.ilike('CREDIT')).scalar() or 0
    _vend_paid = db.session.query(func.sum(VendPay.amount))\
        .filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    payables = max(_credit_purchases - _vend_paid, 0)
    total_liabilities = payables
    
    # 3. Equity — read directly from ShareInvestment/ShareWithdrawal for accuracy
    from app.models import ShareInvestment as SI, ShareWithdrawal as SW
    total_invested   = db.session.query(func.sum(SI.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_withdrawn  = db.session.query(func.sum(SW.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    equity_capital   = total_invested - total_withdrawn
    
    summary = AccountingService.get_financial_summary(current_user.tenant_id)
    net_profit = summary['net_profit']
    total_equity = equity_capital + net_profit
    
    # 4. Detailed Breakdown (Receivables & Payables per person)
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    detailed_receivables = []
    total_detailed_receivables = 0
    for c in customers:
        c_sales = db.session.query(func.sum(Sale.total_amount))\
            .filter(Sale.customer_id == c.id, Sale.tenant_id == current_user.tenant_id, Sale.payment_method.ilike('Credit'))\
            .scalar() or 0
        c_payments = db.session.query(func.sum(CustomerPayment.amount)).filter_by(customer_id=c.id, tenant_id=current_user.tenant_id).scalar() or 0
        
        # Include ALL returns for this customer
        from app.models import SaleReturn
        c_returns = db.session.query(func.sum(SaleReturn.total_amount))\
            .join(Sale).filter(Sale.customer_id == c.id, Sale.tenant_id == current_user.tenant_id)\
            .scalar() or 0
            
        c_balance = c_sales - c_payments - c_returns
        if c_balance > 0:
            detailed_receivables.append({'name': c.name, 'balance': c_balance})
            total_detailed_receivables += c_balance
    receivables = max(receivables, total_detailed_receivables)

    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    detailed_payables = []
    total_detailed_payables = 0
    for v in vendors:
        v_purchases = db.session.query(func.sum(Purchase.total_amount))\
            .filter(Purchase.vendor_id == v.id, Purchase.tenant_id == current_user.tenant_id, Purchase.payment_method.ilike('CREDIT'))\
            .scalar() or 0
        v_payments = db.session.query(func.sum(VendorPayment.amount)).filter_by(vendor_id=v.id, tenant_id=current_user.tenant_id).scalar() or 0
        
        # Include ALL returns for this vendor to ensure debt is reduced as expected
        from app.models import PurchaseReturn
        v_returns = db.session.query(func.sum(PurchaseReturn.total_amount))\
            .join(Purchase).filter(Purchase.vendor_id == v.id, Purchase.tenant_id == current_user.tenant_id)\
            .scalar() or 0
            
        v_balance = v_purchases - v_payments - v_returns
        if v_balance > 0:
            detailed_payables.append({'name': v.name, 'balance': v_balance})
            total_detailed_payables += v_balance
    # Final Consistency Check: The header totals must match the sum of the detailed parts
    receivables = total_detailed_receivables
    payables = total_detailed_payables
    
    total_liabilities = payables
    total_assets = total_bank_balance + receivables + inventory_value + other_assets_value

    shareholders = Shareholder.query.filter_by(tenant_id=current_user.tenant_id).all()
    detailed_equity = []
    for s in shareholders:
        s_investments = db.session.query(func.sum(ShareInvestment.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        s_withdrawals = db.session.query(func.sum(ShareWithdrawal.amount)).filter_by(shareholder_id=s.id).scalar() or 0
        s_balance = s_investments - s_withdrawals
        detailed_equity.append({'name': s.name, 'balance': s_balance})

    return render_template('accounting/balance_sheet.html',
                           bank_data=bank_data,
                           total_bank_balance=total_bank_balance,
                           receivables=receivables,
                           detailed_receivables=detailed_receivables,
                           detailed_payables=detailed_payables,
                           detailed_equity=detailed_equity,
                           inventory_value=inventory_value,
                           other_assets_value=other_assets_value,
                           total_assets=total_assets,
                           payables=payables,
                           total_liabilities=total_liabilities,
                           equity_capital=equity_capital,
                           net_profit=net_profit,
                           total_equity=total_equity)

@accounting.route('/accounting/other-income', methods=['GET', 'POST'])
@login_required
def other_income():
    from app.models import OtherIncome, ChartAccount
    from datetime import datetime
    
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category') # Account Code for Revenue
        account = request.form.get('account')   # Account Code for Asset
        income_date_str = request.form.get('income_date')
        
        income_date = datetime.utcnow()
        if income_date_str:
            try:
                income_date = datetime.strptime(income_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        new_income = OtherIncome(
            description=description,
            amount=float(amount) if amount else 0.0,
            category=category,
            account=account,
            income_date=income_date,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_income)
        db.session.flush()

        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_income(new_income)

        db.session.commit()
        flash('Other Income recorded successfully!', 'success')
        return redirect(url_for('accounting.other_income'))
        
    all_incomes = OtherIncome.query.filter_by(tenant_id=current_user.tenant_id).order_by(OtherIncome.created_at.desc()).all()
    revenue_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='REVENUE', is_active=True).all()
    
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    bank_accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    return render_template('accounting/other_income.html', 
                           incomes=all_incomes, 
                           revenue_accounts=revenue_accounts, 
                           bank_accounts=bank_accounts)

@accounting.route('/accounting/assets', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def assets():
    if request.method == 'POST':
        name = request.form.get('name')
        value = request.form.get('value')
        desc = request.form.get('description')
        depreciation_method = request.form.get('depreciation_method', 'None')
        useful_life_years = request.form.get('useful_life_years', 0)
        salvage_value = request.form.get('salvage_value', 0)
        
        new_asset = Asset(
            name=name,
            value=float(value),
            description=desc,
            depreciation_method=depreciation_method,
            useful_life_years=int(useful_life_years) if useful_life_years else 0,
            salvage_value=float(salvage_value) if salvage_value else 0.0,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_asset)
        db.session.commit()
        flash('Asset recorded!', 'success')
        return redirect(url_for('accounting.assets'))
        
    all_assets = Asset.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('accounting/assets.html', assets=all_assets, current_time=datetime.utcnow())

@accounting.route('/accounting/bank-accounts', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def bank_accounts():
    if request.method == 'POST':
        name = request.form.get('account_name')
        number = request.form.get('account_number')
        initial = request.form.get('initial_balance')
        
        new_bank = BankAccount(
            account_name=name,
            account_number=number,
            initial_balance=float(initial or 0),
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_bank)
        db.session.commit()
        flash('Bank account added!', 'success')
        return redirect(url_for('accounting.bank_accounts'))
        
    from app.services.accounting_service import AccountingService
    # Fetch accounts from Chart of Accounts that are liquid (Cash & Bank)
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    liquid_accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    accounts_with_balance = []
    for acc in liquid_accounts:
        balance = AccountingService.get_account_balance(acc.id, current_user.tenant_id)
        accounts_with_balance.append({
            'id': acc.id,
            'account_name': acc.account_name,
            'account_code': acc.account_code,
            'current_balance': balance
        })
        
    return render_template('accounting/bank_accounts.html', accounts=accounts_with_balance)

@accounting.route('/accounting/bank-account/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def edit_bank_account(id):
    account = ChartAccount.query.get_or_404(id)
    if account.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        account.account_name = data.get('name')
        account.account_code = data.get('code')
        account.sub_category = data.get('sub_category')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/bank-account/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_bank_account(id):
    account = ChartAccount.query.get_or_404(id)
    if account.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        account.is_active = False # Soft delete
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/bank-transfer', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def bank_transfer():
    if request.method == 'POST':
        from_id = request.form.get('from_account_id')
        to_id = request.form.get('to_account_id')
        amount = request.form.get('amount')
        desc = request.form.get('description')
        
        new_transfer = BankTransfer(
            from_account_id=from_id,
            to_account_id=to_id,
            amount=float(amount),
            description=desc,
            tenant_id=current_user.tenant_id
        )
        db.session.add(new_transfer)
        db.session.commit()
        
        # Professional Accounting Integration
        from app.services.accounting_service import AccountingService
        AccountingService.record_bank_transfer(new_transfer)
        
        flash('Transfer recorded!', 'success')
        return redirect(url_for('accounting.bank_transfer'))
        
    transfers = BankTransfer.query.filter_by(tenant_id=current_user.tenant_id).order_by(BankTransfer.transfer_date.desc()).all()
    # Professional Dynamic Filtering for Liquid Assets
    all_assets = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category='ASSETS', is_active=True).all()
    accounts = [a for a in all_assets if a.sub_category in ['Bank Accounts', 'Cash & Bank', 'Current Assets']]
    
    return render_template('accounting/bank_transfer.html', transfers=transfers, accounts=accounts)

@accounting.route('/accounting/bank-transfer/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def edit_bank_transfer(id):
    transfer = BankTransfer.query.get_or_404(id)
    if transfer.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    data = request.get_json()
    try:
        transfer.from_account_id = int(data.get('from_account_id'))
        transfer.to_account_id   = int(data.get('to_account_id'))
        transfer.amount          = float(data.get('amount'))
        transfer.description     = data.get('description', '')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Transfer updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/bank-transfer/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_bank_transfer(id):
    transfer = BankTransfer.query.get_or_404(id)
    if transfer.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        db.session.delete(transfer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Transfer deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/reports/sales')
@login_required
def sales_report():
    from app.models import Sale, SaleItem
    # Fetch all sales for the tenant
    sales = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all()
    total_sales = sum(s.total_amount for s in sales)
    return render_template('accounting/sales_report.html', sales=sales, total_sales=total_sales)

@accounting.route('/accounting/reports/sales/pdf')
@login_required
@roles_required('admin', 'accountant', 'developer')
def export_sales_pdf():
    sales = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all()
    total_sales = sum(s.total_amount for s in sales)
    
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'tenant': tenant,
        'report_name': 'Sales Activity Report',
        'now': datetime.utcnow(),
        'current_user': current_user
    }
    
    from app.utils.audit import log_audit
    log_audit('EXPORT_PDF', 'ACCOUNTING', 'Exported sales report to PDF')
    
    return ReportingService.generate_pdf('reports/sales_report_pdf.html', context, f"sales_report_{datetime.now().strftime('%Y%m%d')}.pdf")

@accounting.route('/accounting/reports/sales/excel')
@login_required
@roles_required('admin', 'accountant', 'developer')
def export_sales_excel():
    sales = Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all()
    
    data = []
    for s in sales:
        data.append([
            s.invoice_no,
            s.customer.name if s.customer else 'Walk-in',
            s.payment_method,
            s.total_amount,
            s.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    columns = ['Invoice #', 'Customer', 'Payment Method', 'Total Amount', 'Date']
    
    from app.utils.audit import log_audit
    log_audit('EXPORT_EXCEL', 'ACCOUNTING', 'Exported sales list to Excel')
    
    return ReportingService.generate_excel(data, columns, f"sales_report_{datetime.now().strftime('%Y%m%d')}.xlsx")

@accounting.route('/accounting/reports/financial')
@login_required
@roles_required('admin', 'accountant', 'developer')
def financial_report():
    from app.services.accounting_service import AccountingService
    summary = AccountingService.get_financial_summary(current_user.tenant_id)
    
    return render_template('accounting/financial_report.html',
                           total_revenue=summary['revenue'],
                           total_cogs=summary['cogs'],
                           gross_profit=summary['revenue'] - summary['cogs'],
                           total_expenses=summary['expenses'],
                           total_other_income=summary['other_income'],
                           net_profit=summary['net_profit'])

@accounting.route('/accounting/reports/financial/pdf')
@login_required
@roles_required('admin', 'accountant', 'developer')
def export_financial_pdf():
    from app.models import Sale, SaleItem, Expense, OtherIncome, Tenant
    from sqlalchemy import func
    
    total_revenue = db.session.query(func.sum(Sale.total_amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    sold_items = db.session.query(SaleItem).join(Sale).filter(Sale.tenant_id == current_user.tenant_id).all()
    total_cogs = sum(item.quantity * item.buy_price for item in sold_items)
    gross_profit = total_revenue - total_cogs
    total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_other_income = db.session.query(func.sum(OtherIncome.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_profit = (gross_profit + total_other_income) - total_expenses
    
    tenant = Tenant.query.get(current_user.tenant_id)
    
    context = {
        'total_revenue': total_revenue,
        'total_cogs': total_cogs,
        'gross_profit': gross_profit,
        'total_expenses': total_expenses,
        'total_other_income': total_other_income,
        'net_profit': net_profit,
        'tenant': tenant,
        'report_name': 'Profit & Loss Statement',
        'now': datetime.utcnow(),
        'current_user': current_user
    }
    
    from app.utils.audit import log_audit
    log_audit('EXPORT_PDF', 'ACCOUNTING', 'Exported Profit & Loss report to PDF')
    
    return ReportingService.generate_pdf('reports/financial_report_pdf.html', context, f"profit_loss_{datetime.now().strftime('%Y%m%d')}.pdf")

@accounting.route('/accounting/reports/contact-statement')
@login_required
@roles_required('admin', 'accountant', 'developer', 'manager')
def contact_statement():
    from app.models import Customer, Vendor, Sale, Purchase, CustomerPayment, VendorPayment, SaleReturn, PurchaseReturn
    from sqlalchemy import func
    
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    suppliers = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    contact_type = request.args.get('type', '')
    contact_id = request.args.get('contact_id', type=int)
    date_range = request.args.get('date_range', '')
    
    statement_data = []
    opening_balance = 0
    closing_balance = 0
    contact_info = None
    start_date = None
    end_date = None
    
    if contact_type and contact_id and date_range:
        try:
            dates = date_range.split(' - ')
            start_date = datetime.strptime(dates[0], '%d/%m/%Y')
            # Set end date to end of the day
            end_date = datetime.strptime(dates[1], '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        except Exception:
            start_date = datetime(datetime.today().year, 1, 1)
            end_date = datetime(datetime.today().year, 12, 31, 23, 59, 59)
            
        if contact_type == 'customer':
            contact_info = Customer.query.get(contact_id)
            if contact_info and contact_info.tenant_id == current_user.tenant_id:
                # Calculate Opening Balance (before start_date)
                # Sales (Debit)
                sales_before = db.session.query(func.sum(Sale.total_amount)).filter(Sale.customer_id == contact_id, Sale.created_at < start_date).scalar() or 0
                # Payments (Credit)
                payments_before = db.session.query(func.sum(CustomerPayment.amount)).filter(CustomerPayment.customer_id == contact_id, CustomerPayment.created_at < start_date).scalar() or 0
                # Returns (Credit)
                # (Assuming Returns have customer_id or link to Sale)
                # For simplicity, if SaleReturn doesn't have customer_id easily accessible, join with Sale
                returns_before = db.session.query(func.sum(SaleReturn.total_amount)).join(Sale).filter(Sale.customer_id == contact_id, SaleReturn.created_at < start_date).scalar() or 0
                
                opening_balance = sales_before - payments_before - returns_before
                running_balance = opening_balance
                
                # Fetch Transactions within date range
                transactions = []
                
                sales = Sale.query.filter(Sale.customer_id == contact_id, Sale.created_at >= start_date, Sale.created_at <= end_date).all()
                for s in sales:
                    transactions.append({'date': s.created_at, 'ref': s.invoice_no, 'desc': 'Sales Invoice', 'debit': s.total_amount, 'credit': 0, 'type': 'invoice'})
                    
                payments = CustomerPayment.query.filter(CustomerPayment.customer_id == contact_id, CustomerPayment.created_at >= start_date, CustomerPayment.created_at <= end_date).all()
                for p in payments:
                    transactions.append({'date': p.created_at, 'ref': p.reference_no or 'PAY', 'desc': f'Payment ({p.payment_method})', 'debit': 0, 'credit': p.amount, 'type': 'payment'})
                    
                returns = SaleReturn.query.join(Sale).filter(Sale.customer_id == contact_id, SaleReturn.created_at >= start_date, SaleReturn.created_at <= end_date).all()
                for r in returns:
                    transactions.append({'date': r.created_at, 'ref': r.invoice_no, 'desc': 'Sales Return', 'debit': 0, 'credit': r.total_amount, 'type': 'return'})
                
                transactions.sort(key=lambda x: x['date'])
                
                for t in transactions:
                    running_balance += t['debit'] - t['credit']
                    t['balance'] = running_balance
                    statement_data.append(t)
                    
                closing_balance = running_balance
                
        elif contact_type == 'supplier':
            contact_info = Vendor.query.get(contact_id)
            if contact_info and contact_info.tenant_id == current_user.tenant_id:
                # Supplier: We owe them. Purchases = Credit, Payments = Debit. 
                # But to match UI standard in screenshot (Debit/Invoice, Credit/Payment), we might just show Debit=Invoice, Credit=Payment and negative balance if we owe.
                # Actually, standard Account Statement for supplier: Invoice is Credit, Payment is Debit.
                # Let's use the UI columns: "Debit", "Credit". 
                # If we put Purchase in Credit, Balance increases (Credit balance). 
                
                purchases_before = db.session.query(func.sum(Purchase.total_amount)).filter(Purchase.vendor_id == contact_id, Purchase.created_at < start_date).scalar() or 0
                payments_before = db.session.query(func.sum(VendorPayment.amount)).filter(VendorPayment.vendor_id == contact_id, VendorPayment.created_at < start_date).scalar() or 0
                returns_before = db.session.query(func.sum(PurchaseReturn.total_amount)).join(Purchase).filter(Purchase.vendor_id == contact_id, PurchaseReturn.created_at < start_date).scalar() or 0
                
                opening_balance = purchases_before - payments_before - returns_before
                running_balance = opening_balance
                
                transactions = []
                purchases = Purchase.query.filter(Purchase.vendor_id == contact_id, Purchase.created_at >= start_date, Purchase.created_at <= end_date).all()
                for p in purchases:
                    # For Supplier, Purchase increases what we owe. Let's put it in Debit to match the Invoice column, but logically it's a Credit.
                    # Screenshot says "Debit" and "Credit". If it's a supplier, "Debit" might still mean the Bill.
                    transactions.append({'date': p.created_at, 'ref': p.invoice_no, 'desc': 'Purchase Invoice', 'debit': p.total_amount, 'credit': 0, 'type': 'invoice'})
                    
                payments = VendorPayment.query.filter(VendorPayment.vendor_id == contact_id, VendorPayment.created_at >= start_date, VendorPayment.created_at <= end_date).all()
                for p in payments:
                    transactions.append({'date': p.created_at, 'ref': p.reference_no or 'PAY', 'desc': f'Payment ({p.payment_method})', 'debit': 0, 'credit': p.amount, 'type': 'payment'})
                    
                returns = PurchaseReturn.query.join(Purchase).filter(Purchase.vendor_id == contact_id, PurchaseReturn.created_at >= start_date, PurchaseReturn.created_at <= end_date).all()
                for r in returns:
                    transactions.append({'date': r.created_at, 'ref': r.invoice_no, 'desc': 'Purchase Return', 'debit': 0, 'credit': r.total_amount, 'type': 'return'})
                    
                transactions.sort(key=lambda x: x['date'])
                
                for t in transactions:
                    # Balance = Invoices - Payments
                    running_balance += t['debit'] - t['credit']
                    t['balance'] = running_balance
                    statement_data.append(t)
                    
                closing_balance = running_balance

    return render_template('accounting/contact_statement.html',
                           customers=customers,
                           suppliers=suppliers,
                           contact_type=contact_type,
                           contact_id=contact_id,
                           date_range=date_range,
                           contact_info=contact_info,
                           statement_data=statement_data,
                           opening_balance=opening_balance,
                           closing_balance=closing_balance,
                           start_date=start_date,
                           end_date=end_date,
                           now=datetime.utcnow())

def calculate_ageing_buckets(invoices, total_credits, now):
    buckets = {'current': 0, 'd_1_30': 0, 'd_31_60': 0, 'd_61_90': 0, 'd_91_plus': 0, 'total': 0}
    unpaid_invoices = []
    
    for inv in invoices:
        if total_credits >= inv.total_amount:
            total_credits -= inv.total_amount
            continue
        
        balance = inv.total_amount - total_credits
        total_credits = 0
        
        age = (now - inv.created_at).days
        
        # Assuming due date is created_at
        if age <= 0:
            buckets['current'] += balance
            bucket_name = 'Current'
        elif 1 <= age <= 30:
            buckets['d_1_30'] += balance
            bucket_name = '1 - 30 days past due'
        elif 31 <= age <= 60:
            buckets['d_31_60'] += balance
            bucket_name = '31 - 60 days past due'
        elif 61 <= age <= 90:
            buckets['d_61_90'] += balance
            bucket_name = '61 - 90 days past due'
        else:
            buckets['d_91_plus'] += balance
            bucket_name = '91 days and over past due'
            
        buckets['total'] += balance
        unpaid_invoices.append({
            'date': inv.created_at,
            'invoice_no': inv.invoice_no,
            'customer_name': inv.customer.name if hasattr(inv, 'customer') and inv.customer else (inv.vendor.name if hasattr(inv, 'vendor') and inv.vendor else 'Unknown'),
            'due_date': inv.created_at, # Using created_at as due date
            'balance': balance,
            'bucket_name': bucket_name,
            'age': age
        })
        
    return buckets, unpaid_invoices

@accounting.route('/accounting/reports/ageing-receivable-summary')
@login_required
@roles_required('admin', 'accountant', 'developer')
def ageing_receivable_summary():
    now = datetime.utcnow()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    report_data = []
    totals = {'current': 0, 'd_1_30': 0, 'd_31_60': 0, 'd_61_90': 0, 'd_91_plus': 0, 'total': 0}
    
    for c in customers:
        payments = db.session.query(db.func.sum(CustomerPayment.amount)).filter_by(customer_id=c.id).scalar() or 0
        returns = db.session.query(db.func.sum(SaleReturn.total_amount)).join(Sale).filter(Sale.customer_id==c.id).scalar() or 0
        total_credits = payments + returns
        
        invoices = Sale.query.filter_by(customer_id=c.id).order_by(Sale.created_at.asc()).all()
        buckets, _ = calculate_ageing_buckets(invoices, total_credits, now)
        
        if buckets['total'] > 0:
            report_data.append({
                'customer_name': c.name,
                'buckets': buckets
            })
            for k in totals:
                totals[k] += buckets[k]
                
    return render_template('accounting/ageing_receivable_summary.html', data=report_data, totals=totals, now=now)

@accounting.route('/accounting/reports/ageing-receivable-details')
@login_required
@roles_required('admin', 'accountant', 'developer')
def ageing_receivable_details():
    now = datetime.utcnow()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    detailed_data = {
        'Current': [],
        '1 - 30 days past due': [],
        '31 - 60 days past due': [],
        '61 - 90 days past due': [],
        '91 days and over past due': []
    }
    
    for c in customers:
        payments = db.session.query(db.func.sum(CustomerPayment.amount)).filter_by(customer_id=c.id).scalar() or 0
        returns = db.session.query(db.func.sum(SaleReturn.total_amount)).join(Sale).filter(Sale.customer_id==c.id).scalar() or 0
        total_credits = payments + returns
        
        invoices = Sale.query.filter_by(customer_id=c.id).order_by(Sale.created_at.asc()).all()
        _, unpaid_invoices = calculate_ageing_buckets(invoices, total_credits, now)
        
        for inv in unpaid_invoices:
            detailed_data[inv['bucket_name']].append(inv)
            
    return render_template('accounting/ageing_receivable_details.html', detailed_data=detailed_data, now=now)

@accounting.route('/accounting/reports/ageing-payable-summary')
@login_required
@roles_required('admin', 'accountant', 'developer')
def ageing_payable_summary():
    now = datetime.utcnow()
    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    report_data = []
    totals = {'current': 0, 'd_1_30': 0, 'd_31_60': 0, 'd_61_90': 0, 'd_91_plus': 0, 'total': 0}
    
    for v in vendors:
        payments = db.session.query(db.func.sum(VendorPayment.amount)).filter_by(vendor_id=v.id).scalar() or 0
        returns = db.session.query(db.func.sum(PurchaseReturn.total_amount)).join(Purchase).filter(Purchase.vendor_id==v.id).scalar() or 0
        total_credits = payments + returns
        
        invoices = Purchase.query.filter_by(vendor_id=v.id).order_by(Purchase.created_at.asc()).all()
        buckets, _ = calculate_ageing_buckets(invoices, total_credits, now)
        
        if buckets['total'] > 0:
            report_data.append({
                'vendor_name': v.name,
                'buckets': buckets
            })
            for k in totals:
                totals[k] += buckets[k]
                
    return render_template('accounting/ageing_payable_summary.html', data=report_data, totals=totals, now=now)

@accounting.route('/accounting/reports/balance-sheet/pdf')
@login_required
@roles_required('admin', 'accountant', 'developer')
def export_balance_sheet_pdf():
    from app.models import BankAccount, Sale, Purchase, Expense, OtherIncome, Asset, ShareInvestment, ShareWithdrawal, Tenant
    from sqlalchemy import func
    
    # Logic similar to balance_sheet route
    bank_balance = db.session.query(func.sum(BankAccount.balance)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    receivables = sum(s.total_amount for s in Sale.query.filter_by(tenant_id=current_user.tenant_id).all()) # Simplified
    payables = sum(p.total_amount for p in Purchase.query.filter_by(tenant_id=current_user.tenant_id).all()) # Simplified
    inventory_value = sum(p.stock_quantity * p.buy_price for p in Product.query.filter_by(tenant_id=current_user.tenant_id).all())
    other_assets = db.session.query(func.sum(Asset.value)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    
    total_assets = bank_balance + receivables + inventory_value + other_assets
    total_liabilities = payables
    
    equity_capital = (db.session.query(func.sum(ShareInvestment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0) - \
                     (db.session.query(func.sum(ShareWithdrawal.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0)
                     
    # Net Profit for Equity
    total_revenue = db.session.query(func.sum(Sale.total_amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    sold_items = db.session.query(SaleItem).join(Sale).filter(Sale.tenant_id == current_user.tenant_id).all()
    total_cogs = sum(item.quantity * item.buy_price for item in sold_items)
    total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_other_income = db.session.query(func.sum(OtherIncome.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_profit = (total_revenue - total_cogs + total_other_income) - total_expenses
    
    total_equity = equity_capital + net_profit
    
    tenant = Tenant.query.get(current_user.tenant_id)
    
    context = {
        'bank_balance': bank_balance,
        'receivables': receivables,
        'inventory_value': inventory_value,
        'other_assets': other_assets,
        'payables': payables,
        'equity_capital': equity_capital,
        'net_profit': net_profit,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'tenant': tenant,
        'report_name': 'Balance Sheet',
        'now': datetime.utcnow(),
        'current_user': current_user
    }
    
    from app.utils.audit import log_audit
    log_audit('EXPORT_PDF', 'ACCOUNTING', 'Exported Balance Sheet to PDF')
    
    return ReportingService.generate_pdf('reports/balance_sheet_pdf.html', context, f"balance_sheet_{datetime.now().strftime('%Y%m%d')}.pdf")

@accounting.route('/accounting/reports/cash-flow')
@login_required
@roles_required('admin', 'accountant', 'developer')
def cash_flow_report():
    from app.models import Sale, CustomerPayment, Purchase, VendorPayment, Expense, OtherIncome, Asset, ShareInvestment, ShareWithdrawal, BankAccount
    from sqlalchemy import func
    
    # Inflows
    cash_sales = db.session.query(func.sum(Sale.total_amount)).filter_by(tenant_id=current_user.tenant_id, payment_method='Cash').scalar() or 0
    customer_payments = db.session.query(func.sum(CustomerPayment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    other_income = db.session.query(func.sum(OtherIncome.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_inflows = cash_sales + customer_payments + other_income
    
    # Outflows
    cash_purchases = db.session.query(func.sum(Purchase.total_amount)).filter_by(tenant_id=current_user.tenant_id, payment_method='Cash').scalar() or 0
    vendor_payments = db.session.query(func.sum(VendorPayment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    expenses = db.session.query(func.sum(Expense.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_outflows = cash_purchases + vendor_payments + expenses
    
    net_operating_cash = total_inflows - total_outflows
    
    # Investing
    asset_purchases = db.session.query(func.sum(Asset.value)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_investing_cash = -asset_purchases
    
    # Financing
    share_investments = db.session.query(func.sum(ShareInvestment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    share_withdrawals = db.session.query(func.sum(ShareWithdrawal.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_financing_cash = share_investments - share_withdrawals
    
    # Net Cash Flow
    net_cash_flow = net_operating_cash + net_investing_cash + net_financing_cash
    
    return render_template('accounting/cash_flow_report.html',
                           cash_sales=cash_sales,
                           customer_payments=customer_payments,
                           other_income=other_income,
                           total_inflows=total_inflows,
                           cash_purchases=cash_purchases,
                           vendor_payments=vendor_payments,
                           expenses=expenses,
                           total_outflows=total_outflows,
                           net_operating_cash=net_operating_cash,
                           asset_purchases=asset_purchases,
                           net_investing_cash=net_investing_cash,
                           share_investments=share_investments,
                           share_withdrawals=share_withdrawals,
                           net_financing_cash=net_financing_cash,
                           net_cash_flow=net_cash_flow)


@accounting.route('/accounting/returns/sales')
@login_required
def returns_sales():
    from app.models import SaleReturn
    returns = SaleReturn.query.filter_by(tenant_id=current_user.tenant_id).order_by(SaleReturn.created_at.desc()).all()
    return render_template('accounting/returns_sales.html', returns=returns)

@accounting.route('/accounting/returns/purchases')
@login_required
def returns_purchases():
    from app.models import PurchaseReturn
    returns = PurchaseReturn.query.filter_by(tenant_id=current_user.tenant_id).order_by(PurchaseReturn.created_at.desc()).all()
    return render_template('accounting/returns_purchases.html', returns=returns)

@accounting.route('/accounting/return/sale/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_sale_return(id):
    from app.models import SaleReturn, Sale, SaleItem, Product, CustomerPayment
    ret = SaleReturn.query.get_or_404(id)
    if ret.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # 1. Reverse Stock and Sale Amount
        # Note: A return can have multiple items, but our current return_sale 
        # records one return header per item return action for simplicity.
        for ret_item in ret.items:
            # Subtract from stock (undoing the "add back to stock")
            product = Product.query.get(ret_item.product_id)
            if product:
                product.stock_quantity -= ret_item.quantity
            
            # Add back to original Sale total
            sale = Sale.query.get(ret.sale_id)
            if sale:
                return_amount = ret_item.quantity * ret_item.unit_price
                sale.total_amount += return_amount
        
        # 2. Delete the Refund Payment
        # Look for the payment record with reference like RETURN-invoice_no
        refund = CustomerPayment.query.filter_by(
            reference_no=f"RETURN-{ret.invoice_no}",
            tenant_id=current_user.tenant_id
        ).first()
        if refund:
            db.session.delete(refund)
            
        # 3. Delete the Return record
        db.session.delete(ret)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Celintii waa la tirtiray, xogtiina waa la saxay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/return/purchase/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_purchase_return(id):
    from app.models import PurchaseReturn, Purchase, PurchaseItem, Product, VendorPayment
    ret = PurchaseReturn.query.get_or_404(id)
    if ret.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # 1. Reverse Stock and Purchase Amount
        for ret_item in ret.items:
            # Add back to stock (undoing the "subtract from stock")
            product = Product.query.get(ret_item.product_id)
            if product:
                product.stock_quantity += ret_item.quantity
            
            # Add back to original Purchase total
            purchase = Purchase.query.get(ret.purchase_id)
            if purchase:
                return_amount = ret_item.quantity * ret_item.unit_cost
                purchase.total_amount += return_amount
        
        # 2. Delete the Refund Payment (Money back)
        refund = VendorPayment.query.filter_by(
            reference_no=f"RETURN-{ret.invoice_no}",
            tenant_id=current_user.tenant_id
        ).first()
        if refund:
            db.session.delete(refund)
            
        # 3. Delete the Return record
        db.session.delete(ret)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Celintii waa la tirtiray, xogtiina waa la saxay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/next-account-code/<category>')
@accounting.route('/accounting/get-next-code')
@login_required
def get_next_code():
    category = request.args.get('category', 'ASSETS')
    sub_category = request.args.get('sub_category')
    
    # Define base ranges for professional grouping
    ranges = {
        'ASSETS': {
            'Cash & Bank': 1000,
            'Accounts Receivable': 1100,
            'Inventory': 1200,
            'Fixed Assets': 1300,
            'Other Assets': 1500,
            '_default': 1000
        },
        'LIABILITIES': {
            'Accounts Payable': 2000,
            'Other Liabilities': 2100,
            '_default': 2000
        },
        'EQUITY': {'_default': 3000},
        'REVENUE': {'_default': 4000},
        'EXPENSES': {'_default': 5000}
    }
    
    cat_range = ranges.get(category, ranges['ASSETS'])
    base = cat_range.get(sub_category, cat_range.get('_default', 1000))
    
    # Find the last account in this specific range
    query = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, category=category)
    if sub_category:
        query = query.filter_by(sub_category=sub_category)
    
    last_acc = query.order_by(ChartAccount.account_code.desc()).first()
    
    if last_acc and last_acc.account_code and last_acc.account_code.isdigit():
        next_code = int(last_acc.account_code) + 1
    else:
        next_code = base + 1
            
    return jsonify({'next_code': str(next_code)})

@accounting.route('/accounting/chart-of-accounts', methods=['GET', 'POST'])
@login_required
def chart_of_accounts():
    from app.models import BankAccount, Asset, ChartAccount
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_acc = ChartAccount(
                account_code=data.get('code'),
                account_name=data.get('name'),
                category=data.get('category'),
                sub_category=data.get('sub_category'),
                notes=data.get('notes'),
                tenant_id=current_user.tenant_id
            )
            db.session.add(new_acc)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Account added successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    # Fetch all custom/seeded accounts
    all_accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    
    # Calculate balances for all accounts at once for efficiency
    from sqlalchemy import func
    from app.models import JournalLine
    
    # Sum debits and credits grouped by account
    balances_query = db.session.query(
        JournalLine.account_id,
        func.sum(JournalLine.debit).label('total_debit'),
        func.sum(JournalLine.credit).label('total_credit')
    ).join(JournalEntry).filter(JournalEntry.tenant_id == current_user.tenant_id).group_by(JournalLine.account_id).all()
    
    balances_map = {b.account_id: (b.total_debit, b.total_credit) for b in balances_query}
    
    # Compute real AR balance: total credit sales - customer payments received
    from app.models import Sale, CustomerPayment
    total_credit_sales = db.session.query(func.sum(Sale.total_amount))\
        .filter_by(tenant_id=current_user.tenant_id, payment_method='Credit').scalar() or 0.0
    total_cust_payments = db.session.query(func.sum(CustomerPayment.amount))\
        .filter_by(tenant_id=current_user.tenant_id).scalar() or 0.0
    real_ar_balance = max(total_credit_sales - total_cust_payments, 0.0)

    # Compute real AP balance: total credit purchases - vendor payments
    from app.models import Purchase, VendorPayment
    total_credit_purchases = db.session.query(func.sum(Purchase.total_amount))\
        .filter_by(tenant_id=current_user.tenant_id, payment_method='CREDIT').scalar() or 0.0
    total_vendor_payments = db.session.query(func.sum(VendorPayment.amount))\
        .filter_by(tenant_id=current_user.tenant_id).scalar() or 0.0
    real_ap_balance = max(total_credit_purchases - total_vendor_payments, 0.0)

    for acc in all_accounts:
        # AR override — use real business data
        if acc.sub_category in ('Accounts Receivable', 'Receivables') or acc.account_code == '1100':
            acc.balance = real_ar_balance
        # AP override — use real business data
        elif acc.sub_category in ('Accounts Payable', 'Payables') or acc.account_code == '2000':
            acc.balance = real_ap_balance
        else:
            debit, credit = balances_map.get(acc.id, (0.0, 0.0))
            if acc.category in ['ASSETS', 'EXPENSES']:
                acc.balance = debit - credit
            else:
                acc.balance = credit - debit
    
    # Categorize strictly by sub_category (mapping database values to UI folders)
    assets = {
        'Cash & Bank': [a for a in all_accounts if a.category == 'ASSETS' and a.sub_category in ['Cash & Bank', 'Bank Accounts', 'Cash']],
        'Accounts Receivable': [a for a in all_accounts if a.category == 'ASSETS' and a.sub_category in ['Accounts Receivable', 'Receivables']],
        'Inventory': [a for a in all_accounts if a.category == 'ASSETS' and a.sub_category == 'Inventory'],
        'Fixed Assets': [a for a in all_accounts if a.category == 'ASSETS' and a.sub_category in ['Fixed Assets', 'Non-current Assets']],
        'Other Assets': [a for a in all_accounts if a.category == 'ASSETS' and a.sub_category not in ['Cash & Bank', 'Bank Accounts', 'Cash', 'Accounts Receivable', 'Receivables', 'Inventory', 'Fixed Assets', 'Non-current Assets']]
    }

    
    # Ensure "Cash on Hand" and other "Current Assets" that are cash-like go to Cash & Bank if not explicitly grouped
    # We can refine this by checking names if needed
    for acc in list(assets['Other Assets']):
        name_lower = acc.account_name.lower()
        if 'cash' in name_lower or 'bank' in name_lower or 'evc' in name_lower or 'plus' in name_lower or 'sahay' in name_lower:
            assets['Cash & Bank'].append(acc)
            assets['Other Assets'].remove(acc)
        elif 'receivable' in name_lower:
            assets['Accounts Receivable'].append(acc)
            assets['Other Assets'].remove(acc)
        elif 'inventory' in name_lower:
            assets['Inventory'].append(acc)
            assets['Other Assets'].remove(acc)


    liabilities = {
        'Accounts Payable': [a for a in all_accounts if a.category == 'LIABILITIES' and a.sub_category in ['Accounts Payable', 'Payables', 'Current Liabilities']],
        'Other Liabilities': [a for a in all_accounts if a.category == 'LIABILITIES' and a.sub_category not in ['Accounts Payable', 'Payables', 'Current Liabilities']]
    }
    
    equity = {
        'Equity & Retained Earnings': [a for a in all_accounts if a.category == 'EQUITY']
    }
    revenue = [a for a in all_accounts if a.category == 'REVENUE']
    expenses = [a for a in all_accounts if a.category == 'EXPENSES']

    
    return render_template('accounting/chart_of_accounts.html', 
                           assets=assets, 
                           liabilities=liabilities, 
                           equity=equity,
                           revenue=revenue,
                           expenses=expenses)

@accounting.route('/accounting/chart-of-accounts/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def edit_chart_account(id):
    acc = ChartAccount.query.get_or_404(id)
    if acc.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    data = request.get_json()
    try:
        acc.category = data.get('category')
        acc.account_code = data.get('code')
        acc.account_name = data.get('name')
        acc.sub_category = data.get('sub_category')
        acc.notes = data.get('notes') # Save notes
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/chart-of-accounts/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_chart_account(id):
    acc = ChartAccount.query.get_or_404(id)
    if acc.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        acc.is_active = False # Soft delete
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/general-journal', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def general_journal():
    from app.models import JournalEntry, JournalLine, ChartAccount
    
    if request.method == 'POST':
        data = request.form
        reference = data.get('reference')
        date_str = data.get('date')
        description = data.get('description')
        
        account_ids = request.form.getlist('account_id[]')
        debits = request.form.getlist('debit[]')
        credits = request.form.getlist('credit[]')
        
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            entry_date = datetime.utcnow()
            
        entry = JournalEntry(
            reference=reference,
            date=entry_date,
            description=description,
            tenant_id=current_user.tenant_id
        )
        db.session.add(entry)
        db.session.flush() # Get entry ID
        
        total_debit = 0.0
        total_credit = 0.0
        
        for i in range(len(account_ids)):
            acc_id = account_ids[i]
            if not acc_id: continue
            
            debit = float(debits[i]) if debits[i] else 0.0
            credit = float(credits[i]) if credits[i] else 0.0
            
            if debit == 0 and credit == 0:
                continue
                
            total_debit += debit
            total_credit += credit
            
            line = JournalLine(
                entry_id=entry.id,
                account_id=acc_id,
                debit=debit,
                credit=credit
            )
            db.session.add(line)
            
        if abs(total_debit - total_credit) > 0.01:
            db.session.rollback()
            flash("Debits and Credits must balance!", "error")
            return redirect(url_for('accounting.general_journal'))
            
        db.session.commit()
        flash("Journal Entry posted successfully!", "success")
        return redirect(url_for('accounting.general_journal'))
        
    entries = JournalEntry.query.filter_by(tenant_id=current_user.tenant_id).order_by(JournalEntry.date.desc()).all()
    accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    return render_template('accounting/general_journal.html', entries=entries, accounts=accounts)
@accounting.route('/accounting/general-journal/<int:id>', methods=['GET'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def get_journal_entry(id):
    from app.models import JournalEntry, JournalLine
    entry = JournalEntry.query.get_or_404(id)
    if entry.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    lines = []
    for line in entry.lines:
        lines.append({
            'account_id': line.account_id,
            'debit': line.debit,
            'credit': line.credit
        })
    
    return jsonify({
        'success': True,
        'entry': {
            'id': entry.id,
            'reference': entry.reference,
            'date': entry.date.strftime('%Y-%m-%d'),
            'description': entry.description,
            'lines': lines
        }
    })

@accounting.route('/accounting/general-journal/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def edit_journal_entry(id):
    from app.models import JournalEntry, JournalLine
    entry = JournalEntry.query.get_or_404(id)
    if entry.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        entry.reference = data.get('reference')
        entry.date = datetime.strptime(data.get('date'), '%Y-%m-%d')
        entry.description = data.get('description')
        
        # Remove old lines
        for line in entry.lines:
            db.session.delete(line)
        
        # Add new lines
        lines_data = data.get('lines', [])
        total_debit = 0.0
        total_credit = 0.0
        
        for line_item in lines_data:
            acc_id = line_item.get('account_id')
            debit = float(line_item.get('debit') or 0)
            credit = float(line_item.get('credit') or 0)
            
            if not acc_id or (debit == 0 and credit == 0):
                continue
                
            total_debit += debit
            total_credit += credit
            
            line = JournalLine(
                entry_id=entry.id,
                account_id=acc_id,
                debit=debit,
                credit=credit
            )
            db.session.add(line)
            
        if abs(total_debit - total_credit) > 0.01:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Debits and credits must balance!'})
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Journal entry updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@accounting.route('/accounting/general-journal/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_journal_entry(id):
    from app.models import JournalEntry
    entry = JournalEntry.query.get_or_404(id)
    if entry.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Journal entry deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@accounting.route('/accounting/general-ledger')
@login_required
@roles_required('admin', 'accountant', 'developer')
def general_ledger():
    from app.models import ChartAccount, JournalLine, JournalEntry
    
    account_id = request.args.get('account_id')
    accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    
    lines = []
    selected_account = None
    if account_id:
        selected_account = ChartAccount.query.get(account_id)
        if selected_account and selected_account.tenant_id == current_user.tenant_id:
            lines = JournalLine.query.filter_by(account_id=account_id).join(JournalEntry).order_by(JournalEntry.date.asc()).all()
            
    return render_template('accounting/general_ledger.html', accounts=accounts, lines=lines, selected_account=selected_account)


# ─── PRINT / PDF REPORT ROUTES ────────────────────────────────────────────────

@accounting.route('/accounting/reports/sales/print')
@login_required
def print_sales_report():
    """Generate a printable Sales Report."""
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'

    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    period    = f"{date_from} → {date_to}" if date_from and date_to else 'All Time'

    query = Sale.query.filter_by(tenant_id=current_user.tenant_id)
    if date_from:
        query = query.filter(Sale.created_at >= date_from)
    if date_to:
        query = query.filter(Sale.created_at <= date_to + ' 23:59:59')
    sales = query.order_by(Sale.created_at.desc()).all()

    return generate_sales_report(sales, business_name=business_name, period=period)


@accounting.route('/accounting/reports/expenses/print')
@login_required
def print_expenses_report():
    """Generate a printable Expenses Report."""
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'

    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    period    = f"{date_from} → {date_to}" if date_from and date_to else 'All Time'

    query = Expense.query.filter_by(tenant_id=current_user.tenant_id)
    if date_from:
        query = query.filter(Expense.created_at >= date_from)
    if date_to:
        query = query.filter(Expense.created_at <= date_to + ' 23:59:59')
    expenses = query.order_by(Expense.created_at.desc()).all()

    return generate_expenses_report(expenses, business_name=business_name, period=period)


@accounting.route('/accounting/reports/financial/print')
@login_required
def print_financial_report():
    """Generate a printable Financial (P&L) Report."""
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'

    # Professional Ledger-based Reporting
    from app.models import JournalLine, ChartAccount
    
    # 1. Total Revenue (Category: REVENUE)
    total_revenue = db.session.query(func.sum(JournalLine.credit - JournalLine.debit))\
        .join(ChartAccount).filter(ChartAccount.category == 'REVENUE', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 2. Total COGS (Category: EXPENSES, Account Name: Cost of Goods Sold)
    total_cogs = db.session.query(func.sum(JournalLine.debit - JournalLine.credit))\
        .join(ChartAccount).filter(ChartAccount.account_name.ilike('%Cost of Goods Sold%'), ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 3. Total Operating Expenses (Category: EXPENSES, excluding COGS)
    total_expenses = db.session.query(func.sum(JournalLine.debit - JournalLine.credit))\
        .join(ChartAccount).filter(ChartAccount.category == 'EXPENSES', ~ChartAccount.account_name.ilike('%Cost of Goods Sold%'), ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 4. Total Other Income (Category: REVENUE, excluding Sales Revenue if desired, but here we include all)
    # Note: If we want to distinguish, we filter by specific codes.
    
    gross_profit = total_revenue - total_cogs
    total_other_income = 0 # Placeholder if separated
    net_profit = gross_profit - total_expenses

    data = {
        'total_revenue':      total_revenue,
        'total_cogs':         total_cogs,
        'gross_profit':       gross_profit,
        'total_expenses':     total_expenses,
        'total_other_income': total_other_income,
        'net_profit':         net_profit,
    }
    return generate_financial_report(data, business_name=business_name)


@accounting.route('/accounting/reports/balance-sheet/print')
@login_required
def print_balance_sheet():
    """Generate a printable Balance Sheet."""
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'

    # Professional Ledger-based Reporting
    from app.models import JournalLine, ChartAccount
    
    # 1. Total Assets (Category: ASSETS)
    total_assets = db.session.query(func.sum(JournalLine.debit - JournalLine.credit))\
        .join(ChartAccount).filter(ChartAccount.category == 'ASSETS', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 2. Total Liabilities (Category: LIABILITIES)
    total_liabilities = db.session.query(func.sum(JournalLine.credit - JournalLine.debit))\
        .join(ChartAccount).filter(ChartAccount.category == 'LIABILITIES', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 3. Equity (Category: EQUITY)
    equity_capital = db.session.query(func.sum(JournalLine.credit - JournalLine.debit))\
        .join(ChartAccount).filter(ChartAccount.category == 'EQUITY', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
        
    # 4. Net Profit (calculated from P&L accounts)
    revenue = db.session.query(func.sum(JournalLine.credit - JournalLine.debit))\
        .join(ChartAccount).filter(ChartAccount.category == 'REVENUE', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
    expenses = db.session.query(func.sum(JournalLine.debit - JournalLine.credit))\
        .join(ChartAccount).filter(ChartAccount.category == 'EXPENSES', ChartAccount.tenant_id == current_user.tenant_id).scalar() or 0
    net_profit = revenue - expenses

    data = {
        'total_bank_balance':  0, # Simplified as part of total_assets in ledger view
        'receivables':         0, # Simplified
        'inventory_value':     0, # Simplified
        'other_assets_value':  0, # Simplified
        'total_assets':        total_assets,
        'payables':            total_liabilities,
        'equity_capital':      equity_capital,
        'net_profit':          net_profit,
    }
    return generate_balance_sheet_report(data, business_name=business_name)


@accounting.route('/accounting/reports/cash-flow/print')
@login_required
def print_cash_flow_report():
    from app.models import Tenant, Sale, CustomerPayment, Purchase, VendorPayment, Expense, OtherIncome, Asset, ShareInvestment, ShareWithdrawal
    from sqlalchemy import func
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'

    cash_sales = db.session.query(func.sum(Sale.total_amount)).filter_by(tenant_id=current_user.tenant_id, payment_method='Cash').scalar() or 0
    customer_payments = db.session.query(func.sum(CustomerPayment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    other_income = db.session.query(func.sum(OtherIncome.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_inflows = cash_sales + customer_payments + other_income
    
    cash_purchases = db.session.query(func.sum(Purchase.total_amount)).filter_by(tenant_id=current_user.tenant_id, payment_method='Cash').scalar() or 0
    vendor_payments = db.session.query(func.sum(VendorPayment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    expenses = db.session.query(func.sum(Expense.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    total_outflows = cash_purchases + vendor_payments + expenses
    net_operating_cash = total_inflows - total_outflows
    
    asset_purchases = db.session.query(func.sum(Asset.value)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_investing_cash = -asset_purchases
    
    share_investments = db.session.query(func.sum(ShareInvestment.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    share_withdrawals = db.session.query(func.sum(ShareWithdrawal.amount)).filter_by(tenant_id=current_user.tenant_id).scalar() or 0
    net_financing_cash = share_investments - share_withdrawals
    
    net_cash_flow = net_operating_cash + net_investing_cash + net_financing_cash

    data = {
        'cash_sales': cash_sales,
        'customer_payments': customer_payments,
        'other_income': other_income,
        'total_inflows': total_inflows,
        'cash_purchases': cash_purchases,
        'vendor_payments': vendor_payments,
        'expenses': expenses,
        'total_outflows': total_outflows,
        'net_operating_cash': net_operating_cash,
        'asset_purchases': asset_purchases,
        'net_investing_cash': net_investing_cash,
        'share_investments': share_investments,
        'share_withdrawals': share_withdrawals,
        'net_financing_cash': net_financing_cash,
        'net_cash_flow': net_cash_flow
    }
    return generate_cash_flow_report(data, business_name=business_name)


@accounting.route('/accounting/reports/inventory/print')
@login_required
def print_inventory_report():
    """Generate a printable Inventory / Stock Report."""
    from app.models import Tenant
    tenant = Tenant.query.get(current_user.tenant_id)
    business_name = tenant.name if tenant else 'Rays Technology'
    products = Product.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    return generate_inventory_report(products, business_name=business_name)

@accounting.route('/accounting/trial-balance')
@login_required
@roles_required('admin', 'accountant', 'developer')
def trial_balance():
    from app.models import ChartAccount, JournalLine
    from sqlalchemy import func
    
    # Get all accounts and their net balances
    accounts = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id).order_by(ChartAccount.account_code).all()
    
    trial_data = []
    total_debit = 0
    total_credit = 0
    
    for acc in accounts:
        debit = db.session.query(func.sum(JournalLine.debit)).filter_by(account_id=acc.id).scalar() or 0
        credit = db.session.query(func.sum(JournalLine.credit)).filter_by(account_id=acc.id).scalar() or 0
        
        if debit > 0 or credit > 0:
            trial_data.append({
                'code': acc.account_code,
                'name': acc.account_name,
                'debit': debit,
                'credit': credit
            })
            total_debit += debit
            total_credit += credit
            
    return render_template('accounting/trial_balance.html', 
                           trial_data=trial_data, 
                           total_debit=total_debit, 
                           total_credit=total_credit)


@accounting.route('/accounting/reports')
@login_required
@roles_required('admin', 'accountant', 'developer', 'manager')
def reports_hub():
    """Central reports index page."""
    return render_template('accounting/reports_hub.html')


@accounting.route('/accounting/transactions')
@login_required
@roles_required('admin', 'accountant', 'developer', 'manager')
def transactions():
    """Unified transactions view with sidebar filtering."""
    from app.models import Sale, Purchase, CustomerPayment, VendorPayment, Expense
    txn_type = request.args.get('type', 'sell')

    rows = []
    if txn_type == 'sell':
        for s in Sale.query.filter_by(tenant_id=current_user.tenant_id).order_by(Sale.created_at.desc()).all():
            rows.append({
                'date': s.created_at.strftime('%d/%m/%Y %H:%M'),
                'ref': s.invoice_no,
                'invoice': s.invoice_no,
                'amount': s.total_amount,
                'type': 'Sell',
                'description': f"Customer: {s.customer.name if s.customer else 'Walk-In Customer'}"
            })
    elif txn_type == 'sales_payments':
        for p in CustomerPayment.query.filter_by(tenant_id=current_user.tenant_id).order_by(CustomerPayment.payment_date.desc()).all():
            rows.append({
                'date': p.payment_date.strftime('%d/%m/%Y %H:%M') if p.payment_date else '--',
                'ref': p.reference_no or '--',
                'invoice': p.reference_no or '--',
                'amount': p.amount,
                'type': 'Sell',
                'description': f"Customer: {p.customer.name if p.customer else 'Walk-In Customer'}"
            })
    elif txn_type == 'purchases':
        for pu in Purchase.query.filter_by(tenant_id=current_user.tenant_id).order_by(Purchase.created_at.desc()).all():
            rows.append({
                'date': pu.created_at.strftime('%d/%m/%Y %H:%M'),
                'ref': pu.invoice_no or '--',
                'invoice': pu.invoice_no or '--',
                'amount': pu.total_amount,
                'type': 'Purchase',
                'description': f"Supplier: {pu.vendor.name if pu.vendor else 'Unknown'}"
            })
    elif txn_type == 'purchase_payments':
        for vp in VendorPayment.query.filter_by(tenant_id=current_user.tenant_id).order_by(VendorPayment.payment_date.desc()).all():
            rows.append({
                'date': vp.payment_date.strftime('%d/%m/%Y %H:%M') if vp.payment_date else '--',
                'ref': vp.reference_no or '--',
                'invoice': vp.reference_no or '--',
                'amount': vp.amount,
                'type': 'Purchase Payment',
                'description': f"Supplier: {vp.vendor.name if vp.vendor else 'Unknown'}"
            })
    elif txn_type == 'expenses':
        for exp in Expense.query.filter_by(tenant_id=current_user.tenant_id).order_by(Expense.created_at.desc()).all():
            rows.append({
                'date': exp.created_at.strftime('%d/%m/%Y %H:%M'),
                'ref': f"EXP-{exp.id:04d}",
                'invoice': f"EXP-{exp.id:04d}",
                'amount': exp.amount,
                'type': 'Expense',
                'description': exp.description
            })

    return render_template('accounting/transactions.html', rows=rows, txn_type=txn_type)
@accounting.route('/accounting/other-income/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'accountant', 'developer')
def delete_other_income(id):
    income = OtherIncome.query.get_or_404(id)
    if income.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Professional Accounting: Clean up journal entries
        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(f"INC-{income.id}", current_user.tenant_id)
        
        db.session.delete(income)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Income record deleted!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
