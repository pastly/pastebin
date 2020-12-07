from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, NoneOf
from app.models import User
from . import MIN_UID, MAX_UID, ANON_UID


class LoginForm(FlaskForm):
    uid = IntegerField(
        'Account ID',
        validators=[NumberRange(MIN_UID, MAX_UID), NoneOf([ANON_UID])])
    submit = SubmitField('Sign In')
