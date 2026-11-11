"""Application factory and shared request safeguards."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine

from .extensions import csrf, db, login_manager


@event.listens_for(Engine, 'connect')
def enable_foreign_keys(connection, _):
    import sqlite3
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


def create_app(test_config=None):
    """Build an app with shared extensions and independently configurable storage."""
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///parenthub.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Set SECRET_KEY in your environment or local .env before starting Flask.')
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Log in to access your private planning.'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except ValueError:
            return None

    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .tracking import bp as tracking_bp
    from .commands import register_commands
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tracking_bp)
    register_commands(app)

    @app.after_request
    def security_headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        return response

    def http_error(error):
        return render_template('error.html', code=error.code), error.code

    for code in (400, 404, 405, 413, 500):
        app.register_error_handler(code, http_error)

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.exception('Database request failed')
        return render_template('error.html', code=503), 503

    return app
