from flask import Blueprint

bp = Blueprint('file', __name__)


from . import routes  # noqa: W0611
