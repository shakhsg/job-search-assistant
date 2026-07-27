"""User model with secure password hashing.

Uses Werkzeug's pbkdf2:sha256 for password storage and Flask-Login's
UserMixin for session management. Maintains relationships to Profile,
Job, and Application models with cascade deletes.

Author: Shukhrat Mirzaev
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """Application user with email-based authentication.

    Attributes:
        email: Unique email address (indexed).
        password_hash: Werkzeug pbkdf2:sha256 hash.
        profile: One-to-one relationship with Profile.
        jobs: One-to-many relationship with Job entries.
        applications: One-to-many relationship with Application entries.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    jobs = db.relationship(
        "Job",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    applications = db.relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def set_password(self, raw_password: str) -> None:
        """Hash and store the given password using pbkdf2:sha256."""
        self.password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256")

    def check_password(self, raw_password: str) -> bool:
        """Verify the given password against the stored hash."""
        return check_password_hash(self.password_hash, raw_password)