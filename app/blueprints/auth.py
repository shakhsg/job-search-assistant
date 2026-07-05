from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.repositories import ProfileRepository


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if not current_app.config["ENABLE_REGISTRATION"]:
        flash("Registration is disabled.", "warning")
        return redirect(url_for("auth.login"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("That email is already in use.", "danger")
        else:
            user = User(email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            ProfileRepository.get_or_create(user)
            login_user(user)
            flash("Account created. Add your profile before scoring jobs.", "success")
            return redirect(url_for("profile.edit_profile"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Signed in successfully.", "success")
            return redirect(url_for("dashboard.index"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
