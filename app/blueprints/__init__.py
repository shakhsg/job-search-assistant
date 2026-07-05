from app.blueprints.auth import auth_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.jobs import jobs_bp
from app.blueprints.materials import materials_bp
from app.blueprints.profile import profile_bp
from app.blueprints.tracker import tracker_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "jobs_bp",
    "materials_bp",
    "profile_bp",
    "tracker_bp",
]
