from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .forms import LoginForm, RegisterForm
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.email.errors.append('This email is already registered. Log in instead.')
            return render_template('form.html', title='Register', form=form), 409
        flash('Account created. Log in to start planning.')
        return redirect(url_for('auth.login'))
    return render_template('form.html', title='Register', form=form), 422 if form.is_submitted() else 200


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data.lower()))
        if user and user.check_password(form.password.data):
            session.clear()
            login_user(user)
            session.permanent = True
            return redirect(url_for('main.dashboard'))
        form.password.errors.append('Email or password is incorrect.')
        return render_template('form.html', title='Log in', form=form), 401
    return render_template('form.html', title='Log in', form=form), 422 if form.is_submitted() else 200


@bp.post('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.guide'))
