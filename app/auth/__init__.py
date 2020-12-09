from flask import Blueprint, current_app
import random
from .. import db
from ..models import User


bp = Blueprint('auth', __name__)

# all UIDs are 16 digit numbers
MIN_UID = 1e15
MAX_UID = 9999999999999999


def new_uid():
    return random.randint(MIN_UID, MAX_UID)


def uid_str(uid: int) -> str:
    s = str(uid)
    return s
    # return f'{s[:4]}-{s[4:8]}-{s[8:12]}-{s[12:]}'


def anon_user():
    u = User.query.filter_by(uid=anon_uid()).first()
    if not u:
        u = User(uid=anon_uid())
        db.session.add(u)
        db.session.commit()
    return User.query.filter_by(uid=anon_uid()).first()


def anon_uid():
    return current_app.config['ANON_UID']


from . import routes, forms  # noqa: W0611
