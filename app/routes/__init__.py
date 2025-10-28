from .auth import auth_bp
from .courses import courses_bp
from .dashboard import dashboard_bp
from .users import users_bp

__all__ = [
    'auth_bp',
    'courses_bp',
    'dashboard_bp',
    'users_bp'
]