from datetime import datetime, timezone

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms import ApplicationStatusForm
from app.repositories import ApplicationRepository
from app.services.export import ExportService


tracker_bp = Blueprint("tracker", __name__, url_prefix="/tracker")


@tracker_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status") or None
    applications = ApplicationRepository.list_for_user(current_user.id, status=status_filter)
    forms = {
        application.id: ApplicationStatusForm(
            status=application.status,
            notes=application.notes,
            manual_review_confirmed=application.manual_review_confirmed,
            manual_submission_confirmed=application.manual_submission_confirmed,
        )
        for application in applications
    }
    return render_template(
        "tracker/index.html",
        applications=applications,
        forms=forms,
        status_filter=status_filter,
    )


@tracker_bp.route("/<int:application_id>/update", methods=["POST"])
@login_required
def update(application_id: int):
    application = ApplicationRepository.get_owned(application_id, current_user.id)
    if application is None:
        abort(404)

    form = ApplicationStatusForm()
    if not form.validate_on_submit():
        flash("Please review the tracker form fields.", "danger")
        return redirect(url_for("tracker.index"))

    requested_status = form.status.data
    if requested_status in {"ready_for_manual_apply", "applied"} and not form.manual_review_confirmed.data:
        flash("Confirm your final review before moving this application forward.", "danger")
        return redirect(url_for("tracker.index"))

    if requested_status == "applied" and not form.manual_submission_confirmed.data:
        flash("You must confirm that you personally submitted the application.", "danger")
        return redirect(url_for("tracker.index"))

    application.status = requested_status
    application.notes = form.notes.data or ""
    application.manual_review_confirmed = form.manual_review_confirmed.data
    application.manual_submission_confirmed = form.manual_submission_confirmed.data
    if requested_status == "applied" and application.submitted_at is None:
        application.submitted_at = datetime.now(timezone.utc)

    from app.extensions import db

    db.session.add(application)
    db.session.commit()
    flash("Tracker updated.", "success")
    return redirect(url_for("tracker.index"))


@tracker_bp.route("/export.csv")
@login_required
def export_csv():
    status_filter = request.args.get("status") or None
    csv_data = ExportService().export_applications_csv(current_user.id, status=status_filter)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )
