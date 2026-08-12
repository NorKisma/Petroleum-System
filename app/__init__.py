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
        from app import models  # noqa: F401

    # Register Blueprints
    from app.modules.auth.routes import auth
    from app.modules.main.routes import main
    from app.modules.staff.routes import staff
    from app.modules.api.routes import api
    from app.modules.customers.routes import customers
    from app.modules.vendor.routes import vendor
    from app.modules.settings.routes import settings
    from app.modules.petroleum.routes import petroleum
    from app.modules.accounting.routes import accounting

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(staff)
    app.register_blueprint(api)
    app.register_blueprint(customers)
    app.register_blueprint(vendor)
    app.register_blueprint(settings)
    app.register_blueprint(petroleum)
    app.register_blueprint(accounting)

    @app.context_processor
    def inject_global_data():
        from datetime import datetime
        from flask_login import current_user
        from app.models import Tenant
        from app.utils.module_access import can_access_module

        company_settings = None
        if current_user.is_authenticated:
            company_settings = Tenant.query.get(current_user.tenant_id)

        def can_access(module_key):
            return can_access_module(current_user, company_settings, module_key)

        from app.utils.module_access import STAFF_MODULE_LABELS

        return {
            'datetime_utcnow': datetime.utcnow,
            'company_settings': company_settings,
            'can_access_module': can_access,
            'staff_module_labels': STAFF_MODULE_LABELS,
        }

    if not app.config.get('TESTING'):
        from app.services.petroleum_scheduler import start_petroleum_scheduler
        start_petroleum_scheduler(app)

    return app
