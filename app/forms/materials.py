from flask_wtf import FlaskForm
from wtforms import SubmitField


class GenerateMaterialsForm(FlaskForm):
    submit = SubmitField("Generate honest application packet")
