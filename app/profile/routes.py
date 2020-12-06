from flask import redirect, url_for, current_app, abort, render_template
from flask_login import login_required, current_user
from . import bp
from ..models import User, UserFile
import os


def probably_image(fname: str) -> bool:
    exts = {'.png', '.jpg', '.jpeg', '.bmp', '.svg', '.gif'}
    _, ext = os.path.splitext(fname)
    return ext.lower() in exts


# Return list of UserFile objects that the given user has recently uploaded
def recent_files(dbuser):
    return UserFile.query.filter_by(user_id=dbuser.id).all()


@bp.route('/', methods=['GET'])
@login_required
def index():
    if not current_user.is_authenticated:
        # should never happen, right?
        return redirect(url_for('misc_routes.index'))
    return render_template(
        'profile/index.html', title='Profile', user=current_user,
        dbuserfiles=recent_files(current_user), probably_image=probably_image)
