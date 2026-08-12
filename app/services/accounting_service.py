from app import db
from app.models import JournalEntry, JournalLine, ChartAccount
from datetime import datetime

class AccountingService:
    @staticmethod
    def get_account(identifier, tenant_id):
        """
        Smart resolver for accounts: works with Account Code (string) or Account ID (int/string ID).
        """
        if not identifier:
            return None
            
        # Try as ID first (if it's numeric or int)
        account = None
        try:
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit() and len(identifier) < 5):
                account = ChartAccount.query.get(int(identifier))
        except:
            pass
            
        # If not found by ID or identifier is a string code (like '1000')
        if not account:
            account = ChartAccount.query.filter_by(account_code=str(identifier), tenant_id=tenant_id).first()
            
        # If still not found, try searching by exact Account Name (handles payment_method like 'EVC Plus')
        if not account:
            search_name = str(identifier)
            if search_name.lower() == 'cash':
                search_name = 'Cash on Hand'
            account = ChartAccount.query.filter(
                ChartAccount.tenant_id == tenant_id,
                db.func.lower(ChartAccount.account_name) == search_name.lower()
            ).first()
            
        return account

    @staticmethod
    def log_transaction(reference, description, tenant_id, lines):
        """
        lines: List of dicts [{'account_code': '1000', 'debit': 100, 'credit': 0}, ...]
        The 'account_code' can be an actual code or an account ID.
        """
        entry = JournalEntry(
            reference=reference,
            description=description,
            tenant_id=tenant_id,
            date=datetime.utcnow()
        )
        db.session.add(entry)
        db.session.flush()

        for line in lines:
            account = AccountingService.get_account(line['account_code'], tenant_id)
            if not account:
                continue
            
            j_line = JournalLine(
                entry_id=entry.id,
                account_id=account.id,
                description=line.get('description', description),
                debit=line.get('debit', 0.0),
                credit=line.get('credit', 0.0)
            )
            db.session.add(j_line)
        
        return entry

    @staticmethod
    def record_sale(sale):
        """
        Automates accounting for a sale:
        1. Debit Cash/Bank/AR (Asset Increase)
        2. Credit Sales (4000) (Revenue Increase)
        3. Debit COGS (5000) (Expense Increase)
        4. Credit Inventory (1200) (Asset Decrease)
        """
        # Determine Payment Account (ID or Code)
        payment_method_raw = sale.payment_method if sale.payment_method else 'Cash'
        
        # Professional Mapping for string-based methods
        if payment_method_raw == 'Credit':
            payment_acc = '1100'
        elif payment_method_raw == 'Cash':
            payment_acc = '1000'
        else:
            payment_acc = payment_method_raw
        
        cogs_amount = sum(item.quantity * (item.buy_price or 0) for item in sale.items)

        cust_name = sale.customer.name if sale.customer else "Walk-in"
        
        lines = [
            {'account_code': payment_acc, 'debit': sale.total_amount, 'credit': 0, 'description': f"Revenue from {sale.invoice_no} ({cust_name})"},
            {'account_code': '4000', 'debit': 0, 'credit': sale.total_amount, 'description': f"Sales Revenue: {sale.invoice_no} ({cust_name})"},
            {'account_code': '5000', 'debit': cogs_amount, 'credit': 0, 'description': f"COGS for {sale.invoice_no}"},
            {'account_code': '1200', 'debit': 0, 'credit': cogs_amount, 'description': f"Inventory deduction for {sale.invoice_no}"}
        ]
        
        AccountingService.log_transaction(
            reference=sale.invoice_no,
            description=f"Sale Invoice: {sale.invoice_no}",
            tenant_id=sale.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_purchase(purchase):
        """
        Automates accounting for a purchase:
        Debit Inventory (1200)
        Credit Cash/Bank/AP
        """
        # Determine Credit Account (Source of funds or Liability)
        credit_account = '2000' # Default Accounts Payable
        if purchase.payment_method == 'CASH':
            credit_account = '1000'
        elif purchase.ap_account:
            credit_account = str(purchase.ap_account) # This can be an ID or Code
        
        lines = [
            {'account_code': '1200', 'debit': purchase.total_amount, 'credit': 0, 'description': f"Inventory increase from {purchase.invoice_no}"},
            {'account_code': credit_account, 'debit': 0, 'credit': purchase.total_amount, 'description': f"Purchase Payment/Liability: {purchase.invoice_no}"}
        ]
        AccountingService.log_transaction(
            reference=purchase.invoice_no,
            description=f"Purchase Invoice: {purchase.invoice_no}",
            tenant_id=purchase.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_expense(expense):
        debit_account = expense.category if expense.category else '5100'
        credit_account = expense.payment_account if expense.payment_account else '1000'

        lines = [
            {'account_code': debit_account, 'debit': expense.amount, 'credit': 0},
            {'account_code': credit_account, 'debit': 0, 'credit': expense.amount}
        ]
        AccountingService.log_transaction(
            reference=f"EXP-{expense.id}",
            description=f"Expense: {expense.description}",
            tenant_id=expense.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_income(income):
        debit_account = income.account if income.account else '1000'
        credit_account = income.category if income.category else '4000'

        lines = [
            {'account_code': debit_account, 'debit': income.amount, 'credit': 0},
            {'account_code': credit_account, 'debit': 0, 'credit': income.amount}
        ]
        AccountingService.log_transaction(
            reference=f"INC-{income.id}",
            description=f"Other Income: {income.description}",
            tenant_id=income.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_customer_payment(payment):
        debit_account = payment.payment_method if payment.payment_method else '1000'
        lines = [
            {'account_code': debit_account, 'debit': payment.amount, 'credit': 0},
            {'account_code': '1100', 'debit': 0, 'credit': payment.amount}
        ]
        AccountingService.log_transaction(
            reference=f"RCPT-{payment.id}",
            description=f"Customer Payment: {payment.customer.name if payment.customer else 'Walk-in'}",
            tenant_id=payment.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_vendor_payment(payment):
        credit_account = payment.payment_method if payment.payment_method else '1000'
        lines = [
            {'account_code': '2000', 'debit': payment.amount, 'credit': 0},
            {'account_code': credit_account, 'debit': 0, 'credit': payment.amount}
        ]
        AccountingService.log_transaction(
            reference=f"VPMT-{payment.id}",
            description=f"Vendor Payment: {payment.vendor.name if payment.vendor else 'Unknown'}",
            tenant_id=payment.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_bank_transfer(transfer):
        from_acc = transfer.from_account
        to_acc = transfer.to_account
        lines = [
            {'account_code': to_acc.account_code, 'debit': transfer.amount, 'credit': 0},
            {'account_code': from_acc.account_code, 'debit': 0, 'credit': transfer.amount}
        ]
        AccountingService.log_transaction(
            reference=f"TRF-{transfer.id}",
            description=f"Internal Transfer: {transfer.description or 'No notes'}",
            tenant_id=transfer.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_share_investment(investment):
        account = investment.account
        # Use account_code (not id) so get_account resolver works correctly
        account_code = account.account_code if account else '1000'
        lines = [
            {'account_code': account_code, 'debit': investment.amount, 'credit': 0,
             'description': f"Investment deposit: {investment.shareholder.name}"},
            {'account_code': '3000', 'debit': 0, 'credit': investment.amount,
             'description': f"Shareholder Equity: {investment.shareholder.name}"}
        ]
        AccountingService.log_transaction(
            reference=f"SH-INV-{investment.id}",
            description=f"Shareholder Investment: {investment.shareholder.name}",
            tenant_id=investment.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_share_withdrawal(withdrawal):
        account = withdrawal.account
        account_code = account.account_code if account else '1000'
        lines = [
            {'account_code': '3000', 'debit': withdrawal.amount, 'credit': 0,
             'description': f"Shareholder Withdrawal: {withdrawal.shareholder.name}"},
            {'account_code': account_code, 'debit': 0, 'credit': withdrawal.amount,
             'description': f"Withdrawal payment: {withdrawal.shareholder.name}"}
        ]
        AccountingService.log_transaction(
            reference=f"SH-WTH-{withdrawal.id}",
            description=f"Shareholder Withdrawal: {withdrawal.shareholder.name}",
            tenant_id=withdrawal.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_return(return_obj, type='SALE'):
        """
        Automates accounting for returns:
        - SALE Return: Debit Revenue (4000), Credit Cash/AR, Debit Inventory (1200), Credit COGS (5000)
        - PURCHASE Return: Debit Cash/AP, Credit Inventory (1200)
        """
        if type == 'SALE':
            sale = return_obj.sale
            payment_method_raw = sale.payment_method if sale.payment_method else 'Cash'
            
            if payment_method_raw == 'Credit':
                payment_acc = '1100'
            elif payment_method_raw == 'Cash':
                payment_acc = '1000'
            else:
                payment_acc = payment_method_raw

            cogs_to_reverse = 0
            for r_item in return_obj.items:
                s_item = next((si for si in sale.items if si.product_id == r_item.product_id), None)
                if s_item:
                    cogs_to_reverse += r_item.quantity * (s_item.buy_price or 0)

            lines = [
                {'account_code': '4000', 'debit': return_obj.total_amount, 'credit': 0, 'description': f"Sales Return: {return_obj.invoice_no}"},
                {'account_code': payment_acc, 'debit': 0, 'credit': return_obj.total_amount, 'description': f"Refund for {return_obj.invoice_no}"},
                {'account_code': '1200', 'debit': cogs_to_reverse, 'credit': 0, 'description': f"Inventory Restock: {return_obj.invoice_no}"},
                {'account_code': '5000', 'debit': 0, 'credit': cogs_to_reverse, 'description': f"COGS Reversal: {return_obj.invoice_no}"}
            ]
            
            AccountingService.log_transaction(
                reference=return_obj.invoice_no,
                description=f"Sale Return: {return_obj.invoice_no}",
                tenant_id=return_obj.tenant_id,
                lines=lines
            )

        elif type == 'PURCHASE':
            purchase = return_obj.purchase
            debit_account = '2000'
            if purchase.payment_method == 'CASH':
                debit_account = '1000'
            elif purchase.ap_account:
                debit_account = str(purchase.ap_account)

            lines = [
                {'account_code': debit_account, 'debit': return_obj.total_amount, 'credit': 0, 'description': f"Return Refund/Credit: {return_obj.invoice_no}"},
                {'account_code': '1200', 'debit': 0, 'credit': return_obj.total_amount, 'description': f"Inventory Reduction: {return_obj.invoice_no}"}
            ]
            
            AccountingService.log_transaction(
                reference=return_obj.invoice_no,
                description=f"Purchase Return: {return_obj.invoice_no}",
                tenant_id=return_obj.tenant_id,
                lines=lines
            )


    @staticmethod
    def record_fuel_sale(sale, fuel_type):
        payment_method_raw = sale.payment_method if sale.payment_method else 'Cash'
        
        if payment_method_raw == 'Credit' or sale.fleet_profile_id:
            payment_acc = '1100'
        elif payment_method_raw == 'Cash' or payment_method_raw == 'Caddaan':
            payment_acc = '1000'
        else:
            payment_acc = payment_method_raw

        # Cost of goods sold based on current average buy price
        cogs_amount = sale.liters_sold * (fuel_type.buy_price or 0)

        cust_name = sale.customer.name if sale.customer else (sale.fleet_profile.customer.name if sale.fleet_profile else "Walk-in")
        
        lines = [
            {'account_code': payment_acc, 'debit': sale.total_amount, 'credit': 0, 'description': f"Revenue from Fuel {sale.invoice_no} ({cust_name})"},
            {'account_code': '4000', 'debit': 0, 'credit': sale.total_amount, 'description': f"Fuel Sales Revenue: {sale.invoice_no}"},
            {'account_code': '5000', 'debit': cogs_amount, 'credit': 0, 'description': f"COGS for Fuel {sale.invoice_no}"},
            {'account_code': '1200', 'debit': 0, 'credit': cogs_amount, 'description': f"Fuel Inventory deduction for {sale.invoice_no}"}
        ]
        
        AccountingService.log_transaction(
            reference=sale.invoice_no,
            description=f"Fuel Sale: {sale.invoice_no}",
            tenant_id=sale.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_fuel_delivery(delivery, payment_method='CREDIT'):
        credit_account = '2000' # Default Accounts Payable
        if delivery.payment_method == 'CASH':
            credit_account = '1000'
        
        lines = [
            {'account_code': '1200', 'debit': delivery.total_cost, 'credit': 0, 'description': f"Fuel Inventory increase from {delivery.delivery_no}"},
            {'account_code': credit_account, 'debit': 0, 'credit': delivery.total_cost, 'description': f"Fuel Delivery Payment/Liability: {delivery.delivery_no}"}
        ]
        AccountingService.log_transaction(
            reference=delivery.delivery_no,
            description=f"Fuel Delivery: {delivery.delivery_no}",
            tenant_id=delivery.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_fuel_dip_variance(dip, tank, fuel_type, variance):
        # Variance is reading - book_stock
        # If variance < 0, it means loss (shrinkage)
        # If variance > 0, it means gain (excess)
        amount = abs(variance * (fuel_type.buy_price or 0))
        if amount <= 0:
            return

        if variance < 0:
            lines = [
                {'account_code': '5100', 'debit': amount, 'credit': 0, 'description': f"Fuel Shrinkage/Loss on Tank {tank.name}"},
                {'account_code': '1200', 'debit': 0, 'credit': amount, 'description': f"Inventory Reduction for Dip {dip.id}"}
            ]
        else:
            lines = [
                {'account_code': '1200', 'debit': amount, 'credit': 0, 'description': f"Inventory Gain for Dip {dip.id}"},
                {'account_code': '4000', 'debit': 0, 'credit': amount, 'description': f"Fuel Excess Gain on Tank {tank.name}"}
            ]

        AccountingService.log_transaction(
            reference=f"DIP-{dip.id}",
            description=f"Fuel Dip Variance: Tank {tank.name}",
            tenant_id=dip.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_fleet_payment(profile, amount, payment_method='Cash', discount=0.0):
        debit_account = payment_method if payment_method else '1000'
        if debit_account.lower() == 'cash':
            debit_account = '1000'

        lines = []
        if amount > 0:
            lines.append({'account_code': debit_account, 'debit': amount, 'credit': 0, 'description': f"Fleet Payment Received: {profile.customer.name}"})
        
        if discount > 0:
            lines.append({'account_code': '4000', 'debit': discount, 'credit': 0, 'description': f"Fleet Discount Given: {profile.customer.name}"})
            
        lines.append({'account_code': '1100', 'debit': 0, 'credit': amount + discount, 'description': f"AR Reduction for {profile.customer.name}"})

        AccountingService.log_transaction(
            reference=f"FLTPAY-{profile.id}-{int(datetime.utcnow().timestamp())}",
            description=f"Fleet Payment: {profile.customer.name}",
            tenant_id=profile.tenant_id,
            lines=lines
        )

    @staticmethod
    def record_fuel_opening_stock(tenant_id, tank_name, liters, unit_cost):
        amount = liters * unit_cost
        if amount <= 0: return
        
        lines = [
            {'account_code': '1200', 'debit': amount, 'credit': 0, 'description': f"Opening Fuel Stock: {tank_name}"},
            {'account_code': '3000', 'debit': 0, 'credit': amount, 'description': f"Owner Equity for {tank_name} stock"}
        ]
        AccountingService.log_transaction(
            reference=f"OPEN-{tank_name.replace(' ', '')}",
            description=f"Initial Fuel Setup: {tank_name}",
            tenant_id=tenant_id,
            lines=lines
        )

    @staticmethod
    def ensure_petroleum_accounts(tenant_id):
        # A utility just to prevent crashes if it is called somewhere.
        pass

    @staticmethod
    def delete_entries(reference, tenant_id):
        entries = JournalEntry.query.filter_by(reference=reference, tenant_id=tenant_id).all()
        for entry in entries:
            JournalLine.query.filter_by(entry_id=entry.id).delete()
            db.session.delete(entry)
        db.session.commit()

    @staticmethod
    def get_account_balance(account_id, tenant_id):
        account = ChartAccount.query.get(account_id)
        if not account or account.tenant_id != tenant_id:
            return 0.0
            
        # --- Direct Query Overrides for Critical Accounts ---
        if account.account_code == '1200' or account.sub_category == 'Inventory':
            from app.models import Product, FuelTank
            pos_inv = db.session.query(db.func.sum(Product.stock_quantity * Product.buy_price)).filter_by(tenant_id=tenant_id).scalar() or 0
            fuel_inv = db.session.query(db.func.sum(FuelTank.current_level * 1.0)).filter_by(tenant_id=tenant_id).scalar() or 0
            # Note: We need a quick way to get average price for fuel tanks. For simplicity in GL, we will just use the fuel type buy_price.
            from app.models import FuelType
            tanks = FuelTank.query.filter_by(tenant_id=tenant_id).all()
            fuel_val = 0
            for t in tanks:
                if t.current_level and t.fuel_type:
                    fuel_val += t.current_level * (t.fuel_type.buy_price or 0)
            return pos_inv + fuel_val

        if account.account_code == '1100' or account.sub_category in ['Accounts Receivable', 'Receivables']:
            from app.models import Sale, CustomerPayment, SaleReturn, FuelSale
            _credit_sales = db.session.query(db.func.sum(Sale.total_amount)).filter_by(tenant_id=tenant_id, payment_method='Credit').scalar() or 0
            _fuel_credit_sales = db.session.query(db.func.sum(FuelSale.total_amount)).filter_by(tenant_id=tenant_id, payment_method='Credit').scalar() or 0
            _cust_paid = db.session.query(db.func.sum(CustomerPayment.amount)).filter_by(tenant_id=tenant_id).scalar() or 0
            
            # Returns only apply to POS sales, not Fuel sales
            _returns = db.session.query(db.func.sum(SaleReturn.total_amount)).join(Sale).filter(Sale.tenant_id == tenant_id, Sale.payment_method == 'Credit').scalar() or 0
            
            return max((_credit_sales + _fuel_credit_sales) - _cust_paid - _returns, 0)
            
        if account.account_code == '2000' or account.sub_category == 'Accounts Payable':
            from app.models import Purchase, VendorPayment, PurchaseReturn
            _credit_purchases = db.session.query(db.func.sum(Purchase.total_amount))\
                .filter_by(tenant_id=tenant_id, payment_method='CREDIT').scalar() or 0
            _vend_paid = db.session.query(db.func.sum(VendorPayment.amount))\
                .filter_by(tenant_id=tenant_id).scalar() or 0
            
            # Only subtract returns where the parent purchase was 'CREDIT'
            _returns = db.session.query(db.func.sum(PurchaseReturn.total_amount))\
                .join(Purchase).filter(Purchase.tenant_id == tenant_id, Purchase.payment_method == 'CREDIT').scalar() or 0
            
            return max(_credit_purchases - _vend_paid - _returns, 0)
            
        if account.account_code == '3000' or account.sub_category == 'Equity':
            from app.models import ShareInvestment, ShareWithdrawal
            total_invested = db.session.query(db.func.sum(ShareInvestment.amount)).filter_by(tenant_id=tenant_id).scalar() or 0
            total_withdrawn = db.session.query(db.func.sum(ShareWithdrawal.amount)).filter_by(tenant_id=tenant_id).scalar() or 0
            return total_invested - total_withdrawn
            
        # --- Default Ledger Calculation ---
        debit_sum = db.session.query(db.func.sum(JournalLine.debit)).filter_by(account_id=account_id).scalar() or 0.0
        credit_sum = db.session.query(db.func.sum(JournalLine.credit)).filter_by(account_id=account_id).scalar() or 0.0
        if account.category in ['ASSETS', 'EXPENSES']:
            return debit_sum - credit_sum
        else:
            return credit_sum - debit_sum

    @staticmethod
    def get_financial_summary(tenant_id):
        revenue = db.session.query(db.func.sum(JournalLine.credit - JournalLine.debit))\
            .join(ChartAccount).filter(ChartAccount.category == 'REVENUE', ChartAccount.tenant_id == tenant_id).scalar() or 0.0
        cogs = db.session.query(db.func.sum(JournalLine.debit - JournalLine.credit))\
            .join(ChartAccount).filter(ChartAccount.account_code == '5000', ChartAccount.tenant_id == tenant_id).scalar() or 0.0
        expenses = db.session.query(db.func.sum(JournalLine.debit - JournalLine.credit))\
            .join(ChartAccount).filter(ChartAccount.category == 'EXPENSES', ChartAccount.account_code != '5000', ChartAccount.tenant_id == tenant_id).scalar() or 0.0
        other_income = db.session.query(db.func.sum(JournalLine.credit - JournalLine.debit))\
            .join(ChartAccount).filter(ChartAccount.category == 'REVENUE', ChartAccount.account_code != '4000', ChartAccount.tenant_id == tenant_id).scalar() or 0.0
        return {
            'revenue': revenue,
            'cogs': cogs,
            'expenses': expenses,
            'other_income': other_income,
            'net_profit': (revenue + other_income) - (cogs + expenses)
        }

    @staticmethod
    def get_monthly_trends(tenant_id):
        from sqlalchemy import extract
        import calendar
        now = datetime.utcnow()
        months_labels = []
        revenue_data = []
        profit_data = []
        for i in range(11, -1, -1):
            m_idx = now.month - i
            y_off = 0
            while m_idx <= 0:
                m_idx += 12
                y_off += 1
            year = now.year - y_off
            month = m_idx
            month_name = calendar.month_name[month][:3]
            months_labels.append(month_name)
            rev = db.session.query(db.func.sum(JournalLine.credit - JournalLine.debit))\
                .join(ChartAccount).join(JournalEntry)\
                .filter(ChartAccount.category == 'REVENUE', 
                        ChartAccount.tenant_id == tenant_id,
                        extract('year', JournalEntry.date) == year,
                        extract('month', JournalEntry.date) == month).scalar() or 0.0
            exp = db.session.query(db.func.sum(JournalLine.debit - JournalLine.credit))\
                .join(ChartAccount).join(JournalEntry)\
                .filter(ChartAccount.category == 'EXPENSES', 
                        ChartAccount.tenant_id == tenant_id,
                        extract('year', JournalEntry.date) == year,
                        extract('month', JournalEntry.date) == month).scalar() or 0.0
            revenue_data.append(rev)
            profit_data.append(rev - exp)
        return {'labels': months_labels, 'revenue': revenue_data, 'profit': profit_data}
