from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, URL

from app.constants import API_PROVIDER_CHOICES


class JobForm(FlaskForm):
    company = StringField("Company", validators=[InputRequired(), Length(max=255)])
    title = StringField("Job title", validators=[InputRequired(), Length(max=255)])
    location = StringField("Location", validators=[Optional(), Length(max=255)])
    employment_type = StringField("Employment type", validators=[Optional(), Length(max=100)])
    compensation = StringField("Compensation", validators=[Optional(), Length(max=255)])
    source_url = StringField("Source URL", validators=[Optional(), URL(), Length(max=500)])
    application_url = StringField("Application URL", validators=[Optional(), URL(), Length(max=500)])
    description_raw = TextAreaField("Job description", validators=[InputRequired(), Length(max=50000)])
    submit = SubmitField("Save job")


class LinkIngestForm(FlaskForm):
    source_url = StringField("Job link", validators=[InputRequired(), URL(), Length(max=500)])
    submit = SubmitField("Import from link")


class CSVIngestForm(FlaskForm):
    csv_file = FileField(
        "CSV file",
        validators=[FileRequired(), FileAllowed(["csv"], "CSV files only.")],
    )
    submit = SubmitField("Import CSV")


class ApiIngestForm(FlaskForm):
    provider_name = SelectField("API provider", choices=API_PROVIDER_CHOICES, validators=[InputRequired()])
    endpoint_url = StringField("Endpoint URL", validators=[InputRequired(), URL(), Length(max=500)])
    submit = SubmitField("Import API jobs")
