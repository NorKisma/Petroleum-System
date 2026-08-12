from app import create_app, db
from app.models import User, Tenant

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"User: {u.username}, Tenant ID: {u.tenant_id}, Tenant Name: {u.tenant.name if u.tenant else 'None'}")
