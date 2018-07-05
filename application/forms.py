from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired


class UserName(FlaskForm):
    artistName = TextField('artistName', [DataRequired()])
    submit = SubmitField("Go")
