from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, NoneOf, Optional
from . import MIN_UID, MAX_UID, ANON_UID


class LoginForm(FlaskForm):
    uid = IntegerField(
        'Account ID',
        validators=[
            NumberRange(MIN_UID, MAX_UID), NoneOf([ANON_UID]), Optional()])
    submit = SubmitField('Sign In')
    register = SubmitField('Create new ID')
