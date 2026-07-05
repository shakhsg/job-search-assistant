from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SubmitField, TextAreaField
from wtforms.validators import Length

from app.constants import APPLICATION_STATUSES


class ApplicationStatusForm(FlaskForm):
    status = SelectField("Status", choices=APPLICATION_STATUSES)
    notes = TextAreaField("Notes", validators=[Length(max=4000)])
    manual_review_confirmed = BooleanField("I reviewed every generated statement")
    manual_submission_confirmed = BooleanField("I personally submitted this application")
    submit = SubmitField("Update tracker")
