from pathlib import Path
from typing import Optional

from flask import Flask

from app.blueprints import auth_bp, dashboard_bp, jobs_bp, materials_bp, profile_bp, tracker_bp
from app.config import BaseConfig
from app.constants import APPLICATION_STATUSES
from app.extensions import csrf, db, login_manager
from app.models import User


def create_app(test_config: Optional[dict] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(BaseConfig)
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    register_template_helpers(app)
    register_blueprints(app)
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id: str):
    if not user_id.isdigit():
        return None
    return db.session.get(User, int(user_id))


def register_template_helpers(app: Flask) -> None:
    @app.template_filter("nl2br")
    def nl2br(value: str) -> str:
        return (value or "").replace("\n", "<br>")

    app.jinja_env.globals["APPLICATION_STATUSES"] = APPLICATION_STATUSES


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(tracker_bp)


def register_cli(app: Flask) -> None:
    from app.services.seed import seed_demo_data

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        seed_demo_data(app)
        print("Seed data created.")
