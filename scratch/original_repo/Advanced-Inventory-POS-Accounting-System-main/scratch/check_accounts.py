from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    accounts = ChartAccount.query.all()
    print("Name | Category | Sub-Category")
    print("-" * 30)
    for a in accounts:
        print(f"{a.account_name} | {a.category} | {a.sub_category}")
