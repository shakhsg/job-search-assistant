from app.extensions import db


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default="review_pending")
    review_ready = db.Column(db.Boolean, nullable=False, default=False)
    manual_review_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    manual_submission_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    notes = db.Column(db.Text, nullable=False, default="")
    resume_draft = db.Column(db.Text, nullable=False, default="")
    cover_letter_draft = db.Column(db.Text, nullable=False, default="")
    screening_answers = db.Column(db.JSON, nullable=False, default=list)
    truthfulness_notes = db.Column(db.Text, nullable=False, default="")
    review_checklist = db.Column(db.JSON, nullable=False, default=list)
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

    user = db.relationship("User", back_populates="applications")
    job = db.relationship("Job", back_populates="application")
