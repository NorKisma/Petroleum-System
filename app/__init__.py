from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from app import models

    # Register Blueprints
    from app.modules.auth.routes import auth
    from app.modules.main.routes import main
    from app.modules.inventory.routes import inventory
    from app.modules.sales.routes import sales
    from app.modules.accounting.routes import accounting
    from app.modules.staff.routes import staff
    from app.modules.api.routes import api
    from app.modules.customers.routes import customers
    from app.modules.vendor.routes import vendor
    from app.modules.share.routes import share
    from app.modules.settings.routes import settings
    from app.modules.ai.routes import ai
    from app.modules.saas.routes import saas
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(inventory)
    app.register_blueprint(sales)
    app.register_blueprint(accounting)
    app.register_blueprint(staff)
    app.register_blueprint(api)
    app.register_blueprint(customers)
    app.register_blueprint(vendor)
    app.register_blueprint(share)
    app.register_blueprint(settings)
    app.register_blueprint(ai)
    app.register_blueprint(saas)
    
    @app.context_processor
    def inject_global_data():
        from datetime import datetime
        from flask_login import current_user
        from app.models import Tenant
        
        company_settings = None
        if current_user.is_authenticated:
            company_settings = Tenant.query.get(current_user.tenant_id)
            
        return {
            'datetime_utcnow': datetime.utcnow,
            'company_settings': company_settings
        }

    return app
