from app import db
from app.models import AuditLog

class Logger:
    @staticmethod
    def log(user_id, action, description, tenant_id):
        """
        Record a system action to the AuditLog table.
        """
        new_log = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            tenant_id=tenant_id
        )
        db.session.add(new_log)
        db.session.commit()
