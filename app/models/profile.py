from app.extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False, default="")
    headline = db.Column(db.String(255), nullable=False, default="")
    email = db.Column(db.String(255), nullable=False, default="")
    phone = db.Column(db.String(100), nullable=False, default="")
    location = db.Column(db.String(255), nullable=False, default="")
    linkedin_url = db.Column(db.String(255), nullable=False, default="")
    portfolio_url = db.Column(db.String(255), nullable=False, default="")
    summary = db.Column(db.Text, nullable=False, default="")
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    work_authorization = db.Column(db.String(255), nullable=False, default="")
    target_roles = db.Column(db.Text, nullable=False, default="")
    preferred_locations = db.Column(db.Text, nullable=False, default="")
    must_have_keywords = db.Column(db.Text, nullable=False, default="")
    avoid_keywords = db.Column(db.Text, nullable=False, default="")
    core_skills = db.Column(db.Text, nullable=False, default="")
    experience_highlights = db.Column(db.Text, nullable=False, default="")
    education = db.Column(db.Text, nullable=False, default="")
    achievements = db.Column(db.Text, nullable=False, default="")
    certifications = db.Column(db.Text, nullable=False, default="")
    answer_bank = db.Column(db.Text, nullable=False, default="")
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

    user = db.relationship("User", back_populates="profile")
