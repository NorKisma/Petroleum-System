from app import create_app, db
from app.models import *

app = create_app()

with app.app_context():
    print("Abuurista miisaska (Creating tables)...")
    db.create_all()
    print("Guul! Miisaskii waa la dhisay.")
