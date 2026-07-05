from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, Length, NumberRange, Optional, URL


class ProfileForm(FlaskForm):
    full_name = StringField("Full name", validators=[Length(max=255)])
    headline = StringField("Headline", validators=[Length(max=255)])
    email = StringField("Contact email", validators=[Optional(), Email(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=100)])
    location = StringField("Base location", validators=[Optional(), Length(max=255)])
    linkedin_url = StringField("LinkedIn URL", validators=[Optional(), URL(), Length(max=255)])
    portfolio_url = StringField("Portfolio URL", validators=[Optional(), URL(), Length(max=255)])
    summary = TextAreaField("Professional summary", validators=[Optional(), Length(max=4000)])
    years_experience = IntegerField("Years of experience", validators=[Optional(), NumberRange(min=0, max=60)])
    work_authorization = StringField("Work authorization", validators=[Optional(), Length(max=255)])
    target_roles = TextAreaField("Target roles", validators=[Optional(), Length(max=2000)])
    preferred_locations = TextAreaField("Preferred locations", validators=[Optional(), Length(max=2000)])
    must_have_keywords = TextAreaField("Must-have keywords", validators=[Optional(), Length(max=2000)])
    avoid_keywords = TextAreaField("Avoid keywords", validators=[Optional(), Length(max=2000)])
    core_skills = TextAreaField("Core skills", validators=[Optional(), Length(max=4000)])
    experience_highlights = TextAreaField("Experience highlights", validators=[Optional(), Length(max=6000)])
    education = TextAreaField("Education", validators=[Optional(), Length(max=3000)])
    achievements = TextAreaField("Achievements", validators=[Optional(), Length(max=4000)])
    certifications = TextAreaField("Certifications", validators=[Optional(), Length(max=2000)])
    answer_bank = TextAreaField("Answer bank", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Save profile")
