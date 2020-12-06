from flask import Blueprint
import random

bp = Blueprint('auth', __name__)

# all UIDs are 16 digit numbers
MIN_UID = 1e15
MAX_UID = 9999999999999999


def new_uid():
    return random.randint(MIN_UID, MAX_UID)


def uid_str(uid: int) -> str:
    s = str(uid)
    return f'{s[:4]}-{s[4:8]}-{s[8:12]}-{s[12:]}'

from . import routes, forms  # noqa: W0611
