from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.constants import APPLICATION_STATUSES
from app.models import Application, Job


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    jobs_query = Job.query.filter_by(user_id=current_user.id)
    applications_query = Application.query.filter_by(user_id=current_user.id)

    status_counts = {
        label: applications_query.filter_by(status=value).count()
        for value, label in APPLICATION_STATUSES
    }

    stats = {
        "jobs": jobs_query.count(),
        "applications": applications_query.count(),
        "high_matches": jobs_query.filter(Job.match_score >= 75).count(),
        "review_pending": applications_query.filter_by(status="review_pending").count(),
    }

    recent_jobs = jobs_query.order_by(Job.updated_at.desc(), Job.created_at.desc()).limit(5).all()
    recent_applications = (
        applications_query.order_by(Application.updated_at.desc(), Application.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        stats=stats,
        status_counts=status_counts,
        recent_jobs=recent_jobs,
        recent_applications=recent_applications,
    )
