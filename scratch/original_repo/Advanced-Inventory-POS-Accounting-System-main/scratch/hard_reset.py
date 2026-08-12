from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    print("Deleting all accounts for tenant 1...")
    ChartAccount.query.filter_by(tenant_id=1).delete()
    db.session.commit()
    print("Reset complete.")
