import re

import pytest

from parenthub import create_app
from parenthub.commands import seed_content
from parenthub.extensions import db


@pytest.fixture
def app(tmp_path):
    application = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-only-secret',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + (tmp_path / 'test.sqlite').as_posix(),
    })
    with application.app_context():
        db.create_all()
        seed_content()
    yield application
    with application.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def token(client, path):
    response = client.get(path, follow_redirects=True)
    assert response.status_code == 200
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.text)
    assert match, response.text
    return match.group(1)


def post(client, path, data=None, source=None, follow_redirects=False):
    return client.post(path, data={**(data or {}), 'csrf_token': token(client, source or path)},
                       follow_redirects=follow_redirects)


def register(client, email='parent@example.com'):
    return post(client, '/auth/register', {'email': email, 'password': 'a secure parent password',
                                         'confirm': 'a secure parent password'})


def login(client, email='parent@example.com'):
    return post(client, '/auth/login', {'email': email, 'password': 'a secure parent password'})


@pytest.fixture
def parent(client):
    assert register(client).status_code == 302
    assert login(client).status_code == 302
    return client
