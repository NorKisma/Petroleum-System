from flask import request
from flask_login import current_user
from app import db
from app.models import AuditLog

def log_audit(action, module=None, description=None):
    """
    Utility function to log user actions for audit trail.
    """
    if not current_user.is_authenticated:
        return
        
    try:
        audit = AuditLog(
            user_id=current_user.id,
            action=action,
            module=module,
            description=description,
            ip_address=request.remote_addr,
            tenant_id=current_user.tenant_id
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to log audit: {e}")
