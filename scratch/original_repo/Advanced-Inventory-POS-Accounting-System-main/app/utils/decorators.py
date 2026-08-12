from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    # Define role equivalence mapping: admin and developer are considered the same
    role_equivalence = {
        "admin": {"admin", "developer"},
        "developer": {"admin", "developer"}
    }
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)  # Not logged in
            # Build the full set of allowed roles, including equivalents
            allowed = set()
            for r in roles:
                allowed.update(role_equivalence.get(r, {r}))
            if current_user.role not in allowed and not getattr(current_user, 'is_super_admin', False):
                abort(403)  # Forbidden: role not permitted
            return f(*args, **kwargs)
        return decorated_function
    return decorator
