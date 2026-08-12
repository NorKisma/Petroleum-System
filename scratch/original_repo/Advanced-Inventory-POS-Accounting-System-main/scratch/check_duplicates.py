from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    accounts = ChartAccount.query.filter_by(tenant_id=1, is_active=True).all()
    for a in accounts:
        print(f"Code: {a.account_code}, Name: {a.account_name}, Sub: {a.sub_category}")
