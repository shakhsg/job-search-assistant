from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.repositories import ApplicationRepository, JobRepository
from app.services.materials import MaterialGenerator


materials_bp = Blueprint("materials", __name__, url_prefix="/materials")


@materials_bp.route("/generate/<int:job_id>", methods=["POST"])
@login_required
def generate(job_id: int):
    job = JobRepository.get_owned(job_id, current_user.id)
    if job is None:
        abort(404)

    try:
        application = MaterialGenerator().generate_for_job(current_user, job)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("jobs.detail", job_id=job.id))

    flash("Generated a review packet. Nothing has been submitted automatically.", "success")
    return redirect(url_for("materials.detail", application_id=application.id))


@materials_bp.route("/<int:application_id>")
@login_required
def detail(application_id: int):
    application = ApplicationRepository.get_owned(application_id, current_user.id)
    if application is None:
        abort(404)
    return render_template("materials/detail.html", application=application)
