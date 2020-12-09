from flask import flash, redirect, request, url_for, render_template
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from .forms import LoginForm
from . import bp, new_uid, uid_str
from .. import db
from ..models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile.index'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.register.data:
            uid = new_uid()
            user = User(uid=uid)
            db.session.add(user)
            db.session.commit()
            flash(f'Account ID {uid_str(uid)} created.')
        else:
            uid = form.uid.data
            user = User.query.filter_by(uid=form.uid.data).first()
        if user is None:
            flash('Invalid account ID')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # if no next GET param, or if it exists and is to a different
            # hostname, then default to this page
            next_page = url_for('profile.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('misc_routes.index'))
