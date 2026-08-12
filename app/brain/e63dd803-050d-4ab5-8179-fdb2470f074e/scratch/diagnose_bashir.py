import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Vendor, Purchase, VendorPayment, PurchaseReturn
from sqlalchemy import func

app = create_app()
with app.app_context():
    vendor = Vendor.query.filter(Vendor.name.ilike('%Bashir Ali%')).first()
    if not vendor:
        print("Vendor 'Bashir Ali' not found.")
    else:
        print(f"--- Diagnostic for Vendor: {vendor.name} (ID: {vendor.id}) ---")
        
        # 1. Purchases
        purchases = Purchase.query.filter_by(vendor_id=vendor.id).all()
        total_p = 0
        print("\nPurchases:")
        for p in purchases:
            print(f"  - INV: {p.invoice_no} | Method: {p.payment_method} | Amount: ${p.total_amount:,.2f} | Date: {p.created_at}")
            if p.payment_method.lower() in ['credit', 'ap']:
                total_p += p.total_amount
        
        # 2. Payments
        payments = VendorPayment.query.filter_by(vendor_id=vendor.id).all()
        total_pay = 0
        print("\nPayments:")
        for pay in payments:
            print(f"  - REF: {pay.reference_no} | Amount: ${pay.amount:,.2f} | Date: {pay.created_at}")
            total_pay += pay.amount
            
        # 3. Returns
        returns = PurchaseReturn.query.join(Purchase).filter(Purchase.vendor_id == vendor.id).all()
        total_ret = 0
        print("\nReturns:")
        for ret in returns:
            print(f"  - INV: {ret.invoice_no} | Amount: ${ret.total_amount:,.2f} | Date: {ret.created_at}")
            total_ret += ret.total_amount
            
        print("\n--- Summary ---")
        print(f"Total Credit Purchases: ${total_p:,.2f}")
        print(f"Total Payments:         ${total_pay:,.2f}")
        print(f"Total Returns:          ${total_ret:,.2f}")
        print(f"CALCULATED BALANCE:     ${(total_p - total_pay - total_ret):,.2f}")
        print("----------------")
