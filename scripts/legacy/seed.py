from app import create_app, db, bcrypt
from app.models import Tenant, User

app = create_app()

def seed_data():
    with app.app_context():
        # 1. Create Tables
        db.create_all()
        
        # 2. Check if Tenant exists
        if not Tenant.query.filter_by(name='Inventory').first():
            new_tenant = Tenant(name='Rays Inventory', subdomain='Inventory')
            db.session.add(new_tenant)
            db.session.commit()
            
            # 3. Create Admin User for this Tenant
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(
                username='Developer',
                email='nor.jws@gmail.com',
                password=hashed_pw,
                role='admin',
                tenant_id=new_tenant.id
            )
            db.session.add(admin_user)
            db.session.commit()
            print("🚀 Demo Data Created! Login: nor.jws@gmail.com / admin123")
        else:
            print("⚠️ Data already exists.")

if __name__ == '__main__':
    seed_data()
