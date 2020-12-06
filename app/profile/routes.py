from flask import redirect, url_for, current_app, abort, render_template
from flask_login import login_required, current_user
from . import bp
from ..models import User


@bp.route('/', methods=['GET'])
@login_required
def index():
    if not current_user.is_authenticated:
        # should never happen, right?
        return redirect(url_for('misc_routes.index'))
    return render_template(
        'profile/index.html', title='Profile', user=current_user)
