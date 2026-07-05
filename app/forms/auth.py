from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=128)])
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[InputRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")
