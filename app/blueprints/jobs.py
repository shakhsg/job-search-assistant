from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms import ApiIngestForm, CSVIngestForm, GenerateMaterialsForm, JobForm, LinkIngestForm
from app.repositories import JobRepository
from app.services.ingest import JobIngestionService
from app.utils.security import UnsafeURLError


jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.route("/", methods=["GET"])
@login_required
def index():
    jobs = JobRepository.list_for_user(current_user.id)
    return render_template(
        "jobs/index.html",
        jobs=jobs,
        job_form=JobForm(),
        link_form=LinkIngestForm(),
        csv_form=CSVIngestForm(),
        api_form=ApiIngestForm(),
    )


@jobs_bp.route("/manual", methods=["POST"])
@login_required
def create_manual():
    form = JobForm()
    if not form.validate_on_submit():
        flash("Please correct the job form fields.", "danger")
        return redirect(url_for("jobs.index"))

    job = JobIngestionService(current_app.config).create_manual_job(current_user, form.data)
    flash(f"Saved {job.title} and parsed the description.", "success")
    return redirect(url_for("jobs.detail", job_id=job.id))


@jobs_bp.route("/ingest/link", methods=["POST"])
@login_required
def ingest_link():
    form = LinkIngestForm()
    if not form.validate_on_submit():
        flash("Enter a valid job URL.", "danger")
        return redirect(url_for("jobs.index"))

    try:
        job = JobIngestionService(current_app.config).ingest_link(current_user, form.source_url.data)
    except (UnsafeURLError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("jobs.index"))
    except Exception as exc:  # pragma: no cover - defensive UI safeguard
        flash(f"Unable to import the link: {exc}", "danger")
        return redirect(url_for("jobs.index"))

    flash(f"Imported {job.title} from the link.", "success")
    return redirect(url_for("jobs.detail", job_id=job.id))


@jobs_bp.route("/ingest/csv", methods=["POST"])
@login_required
def ingest_csv():
    form = CSVIngestForm()
    if not form.validate_on_submit():
        flash("Upload a valid CSV file.", "danger")
        return redirect(url_for("jobs.index"))

    try:
        count = JobIngestionService(current_app.config).ingest_csv(current_user, form.csv_file.data)
    except Exception as exc:  # pragma: no cover - defensive UI safeguard
        flash(f"CSV import failed: {exc}", "danger")
        return redirect(url_for("jobs.index"))

    flash(f"Imported {count} job rows from CSV.", "success")
    return redirect(url_for("jobs.index"))


@jobs_bp.route("/ingest/api", methods=["POST"])
@login_required
def ingest_api():
    form = ApiIngestForm()
    if not form.validate_on_submit():
        flash("Provide a valid provider and endpoint.", "danger")
        return redirect(url_for("jobs.index"))

    try:
        count = JobIngestionService(current_app.config).ingest_api(
            current_user,
            form.provider_name.data,
            form.endpoint_url.data,
        )
    except (UnsafeURLError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("jobs.index"))
    except Exception as exc:  # pragma: no cover - defensive UI safeguard
        flash(f"API import failed: {exc}", "danger")
        return redirect(url_for("jobs.index"))

    flash(f"Imported {count} jobs from the API.", "success")
    return redirect(url_for("jobs.index"))


@jobs_bp.route("/<int:job_id>", methods=["GET", "POST"])
@login_required
def detail(job_id: int):
    job = JobRepository.get_owned(job_id, current_user.id)
    if job is None:
        abort(404)

    form = JobForm(obj=job)
    material_form = GenerateMaterialsForm()
    if form.validate_on_submit():
        job = JobIngestionService(current_app.config).create_manual_job(
            current_user,
            {
                "id": job.id,
                "source_type": job.source_type or "manual",
                "provider_name": job.provider_name,
                "external_id": job.external_id,
                "source_url": form.source_url.data or "",
                "application_url": form.application_url.data or "",
                "company": form.company.data,
                "title": form.title.data,
                "location": form.location.data or "",
                "employment_type": form.employment_type.data or "",
                "compensation": form.compensation.data or "",
                "description_raw": form.description_raw.data,
            },
        )
        flash("Job updated, reparsed, and rescored.", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))

    if request.method == "POST":
        flash("Please correct the job details before saving.", "danger")

    return render_template("jobs/detail.html", job=job, form=form, material_form=material_form)


@jobs_bp.route("/<int:job_id>/refresh", methods=["POST"])
@login_required
def refresh(job_id: int):
    job = JobRepository.get_owned(job_id, current_user.id)
    if job is None:
        abort(404)

    JobIngestionService(current_app.config).refresh_job(current_user, job)
    flash("Job description reparsed and rescored.", "success")
    return redirect(url_for("jobs.detail", job_id=job.id))


@jobs_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete(job_id: int):
    job = JobRepository.get_owned(job_id, current_user.id)
    if job is None:
        abort(404)

    JobRepository.delete(job)
    flash("Job removed.", "info")
    return redirect(url_for("jobs.index"))
