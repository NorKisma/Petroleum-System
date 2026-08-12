from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    cats = db.session.query(ChartAccount.category).distinct().all()
    print(f"Categories in DB: {[c[0] for c in cats]}")
    subs = db.session.query(ChartAccount.sub_category).distinct().all()
    print(f"Sub-categories in DB: {[s[0] for s in subs]}")
