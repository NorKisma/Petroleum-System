import sys
import os
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Sale, Purchase, Expense, OtherIncome, ChartAccount, JournalEntry, JournalLine
from app.services.accounting_service import AccountingService
from datetime import datetime

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting Professional Ledger Migration...")
        
        # 1. Migrate Sales
        sales = Sale.query.all()
        print(f"Migrating {len(sales)} Sales...")
        for s in sales:
            # Check if already exists
            exists = JournalEntry.query.filter_by(reference=s.invoice_no, tenant_id=s.tenant_id).first()
            if not exists:
                AccountingService.record_sale(s)
                print(f"  Record Sale: {s.invoice_no}")
        
        # 2. Migrate Purchases
        purchases = Purchase.query.all()
        print(f"Migrating {len(purchases)} Purchases...")
        for p in purchases:
            exists = JournalEntry.query.filter_by(reference=p.invoice_no, tenant_id=p.tenant_id).first()
            if not exists:
                AccountingService.record_purchase(p)
                print(f"  Record Purchase: {p.invoice_no}")
                
        # 3. Migrate Expenses
        expenses = Expense.query.all()
        print(f"Migrating {len(expenses)} Expenses...")
        for e in expenses:
            ref = f"EXP-{e.id}"
            exists = JournalEntry.query.filter_by(reference=ref, tenant_id=e.tenant_id).first()
            if not exists:
                AccountingService.record_expense(e)
                print(f"  Record Expense: {e.description}")

        # 4. Migrate Other Income
        incomes = OtherIncome.query.all()
        print(f"Migrating {len(incomes)} Other Incomes...")
        for i in incomes:
            ref = f"INC-{i.id}"
            exists = JournalEntry.query.filter_by(reference=ref, tenant_id=i.tenant_id).first()
            if not exists:
                AccountingService.record_income(i)
                print(f"  Record Income: {i.description}")

        db.session.commit()
        print("\nMigration Completed! All past transactions are now connected to the Chart of Accounts.")

if __name__ == "__main__":
    migrate()
