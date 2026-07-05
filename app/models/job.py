from app.extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    source_type = db.Column(db.String(50), nullable=False, default="manual")
    provider_name = db.Column(db.String(50), nullable=False, default="")
    external_id = db.Column(db.String(255), nullable=False, default="")
    source_url = db.Column(db.String(500), nullable=False, default="")
    application_url = db.Column(db.String(500), nullable=False, default="")
    company = db.Column(db.String(255), nullable=False, default="")
    title = db.Column(db.String(255), nullable=False, default="")
    location = db.Column(db.String(255), nullable=False, default="")
    employment_type = db.Column(db.String(100), nullable=False, default="")
    compensation = db.Column(db.String(255), nullable=False, default="")
    description_raw = db.Column(db.Text, nullable=False, default="")
    parsed_data = db.Column(db.JSON, nullable=False, default=dict)
    match_score = db.Column(db.Integer, nullable=False, default=0)
    match_summary = db.Column(db.Text, nullable=False, default="")
    score_details = db.Column(db.JSON, nullable=False, default=dict)
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

    user = db.relationship("User", back_populates="jobs")
    application = db.relationship(
        "Application",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
