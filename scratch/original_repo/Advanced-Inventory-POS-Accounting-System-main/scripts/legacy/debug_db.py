from app import create_app, db
from app.models import User, Tenant, Sale

app = create_app()

with app.app_context():
    users = User.query.all()
    tenants = Tenant.query.all()
    sales = Sale.query.all()
    
    print(f"Total Users: {len(users)}")
    print(f"Total Tenants: {len(tenants)}")
    print(f"Total Sales: {len(sales)}")
    
    for u in users:
        print(f"User: {u.username}, TenantID: {u.tenant_id}, Role: {u.role}")
    
    for s in sales:
        print(f"Sale: {s.invoice_no}, TenantID: {s.tenant_id}, Payment: {s.payment_method}")
