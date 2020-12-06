from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange
from app.models import User
from . import MIN_UID, MAX_UID


class LoginForm(FlaskForm):
    uid = IntegerField(
        'Account ID',
        validators=[InputRequired(), NumberRange(MIN_UID, MAX_UID)])
    submit = SubmitField('Sign In')
