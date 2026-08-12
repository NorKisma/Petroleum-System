import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Sale, Purchase, Expense, OtherIncome, ShareInvestment, ShareWithdrawal, JournalEntry, JournalLine, ChartAccount
from app.services.accounting_service import AccountingService

def migrate_to_gl():
    app = create_app()
    with app.app_context():
        print("--- Bilaabista Migration-ka General Ledger ---")
        
        # 1. Clear existing Journal Entries to avoid duplicates (Optionally)
        # db.session.execute('DELETE FROM journal_lines')
        # db.session.execute('DELETE FROM journal_entries')
        
        # 2. Migrate Sales
        sales = Sale.query.all()
        print(f"Migrating {len(sales)} Sales...")
        for s in sales:
            # Check if already exists
            if not JournalEntry.query.filter_by(reference=s.invoice_no, tenant_id=s.tenant_id).first():
                AccountingService.record_sale(s)
        
        # 3. Migrate Purchases
        purchases = Purchase.query.all()
        print(f"Migrating {len(purchases)} Purchases...")
        for p in purchases:
            if not JournalEntry.query.filter_by(reference=p.invoice_no, tenant_id=p.tenant_id).first():
                AccountingService.record_purchase(p)

        # 4. Migrate Expenses
        expenses = Expense.query.all()
        print(f"Migrating {len(expenses)} Expenses...")
        for e in expenses:
            ref = f"EXP-{e.id}"
            if not JournalEntry.query.filter_by(reference=ref, tenant_id=e.tenant_id).first():
                AccountingService.record_expense(e)

        # 5. Migrate Incomes
        incomes = OtherIncome.query.all()
        print(f"Migrating {len(incomes)} Incomes...")
        for i in incomes:
            ref = f"INC-{i.id}"
            if not JournalEntry.query.filter_by(reference=ref, tenant_id=i.tenant_id).first():
                AccountingService.record_income(i)

        # 6. Migrate Share Transactions
        investments = ShareInvestment.query.all()
        print(f"Migrating {len(investments)} Share Investments...")
        for inv in investments:
            ref = f"SH-INV-{inv.id}"
            if not JournalEntry.query.filter_by(reference=ref, tenant_id=inv.tenant_id).first():
                AccountingService.record_share_investment(inv)
                
        withdrawals = ShareWithdrawal.query.all()
        print(f"Migrating {len(withdrawals)} Share Withdrawals...")
        for w in withdrawals:
            ref = f"SH-WITH-{w.id}"
            if not JournalEntry.query.filter_by(reference=ref, tenant_id=w.tenant_id).first():
                AccountingService.record_share_withdrawal(w)

        # 7. Migrate Bank Transfers
        from app.models import BankTransfer
        transfers = BankTransfer.query.all()
        print(f"Migrating {len(transfers)} Bank Transfers...")
        for t in transfers:
            ref = f"TRF-{t.id}"
            if not JournalEntry.query.filter_by(reference=ref, tenant_id=t.tenant_id).first():
                AccountingService.record_bank_transfer(t)

        db.session.commit()
        print("--- Migration-ka si guul leh ayuu ku dhamaaday! ---")

if __name__ == "__main__":
    migrate_to_gl()
