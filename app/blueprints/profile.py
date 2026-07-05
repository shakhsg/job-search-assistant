from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import ProfileForm
from app.repositories import ProfileRepository
from app.services.scoring import MatchingEngine


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = ProfileRepository.get_or_create(current_user)
    form = ProfileForm(obj=profile)

    if form.validate_on_submit():
        form.populate_obj(profile)
        profile.years_experience = form.years_experience.data or 0
        if not profile.email:
            profile.email = current_user.email
        db.session.add(profile)
        db.session.commit()
        MatchingEngine().refresh_all_for_user(current_user)
        flash("Profile saved and all job scores refreshed.", "success")
        return redirect(url_for("profile.edit_profile"))

    return render_template("profile/edit.html", form=form, profile=profile)
