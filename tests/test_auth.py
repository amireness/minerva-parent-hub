import pytest

from parenthub.extensions import db
from parenthub.models import User
from conftest import login, post, register, token


def test_registration_hash_login_logout(app, client):
    assert register(client, 'Parent@Example.com').status_code == 302
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.email == 'parent@example.com'
        assert user.password_hash != 'a secure parent password'
        assert user.password_hash.startswith('scrypt:')
        assert user.check_password('a secure parent password')
        assert not user.check_password('wrong password')
    response = login(client)
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')
    assert 'HttpOnly' in response.headers['Set-Cookie']
    assert 'SameSite=Lax' in response.headers['Set-Cookie']
    assert client.get('/dashboard').status_code == 200
    assert post(client, '/auth/logout', source='/dashboard').status_code == 302
    assert client.get('/dashboard').status_code == 302


def test_duplicate_and_invalid_credentials(client):
    register(client)
    assert register(client).status_code == 409
    for data in [
        {'email': 'invalid', 'password': 'password', 'confirm': 'password'},
        {'email': 'next@example.com', 'password': 'short', 'confirm': 'short'},
        {'email': 'next@example.com', 'password': 'long password', 'confirm': 'different'},
    ]:
        assert post(client, '/auth/register', data).status_code == 422
    assert post(client, '/auth/login', {'email': 'parent@example.com', 'password': 'wrong'}).status_code == 401
    assert post(client, '/auth/login', {'email': 'nobody@example.com', 'password': 'wrong'}).status_code == 401
    assert client.get('/dashboard').status_code == 302


@pytest.mark.parametrize('path', ['/dashboard', '/checklist', '/reminders', '/reminders/new',
                                 '/questions', '/questions/new', '/reminders/1/edit', '/questions/1/edit'])
def test_protected_gets(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert '/auth/login' in response.location


@pytest.mark.parametrize('path', ['/dashboard', '/checklist/1', '/reminders/new',
                                 '/questions/new', '/reminders/1/delete', '/questions/1/delete', '/auth/logout'])
def test_protected_writes_with_valid_csrf(client, path):
    csrf = token(client, '/auth/login')
    response = client.post(path, data={'csrf_token': csrf})
    assert response.status_code == 302
    assert '/auth/login' in response.location


@pytest.mark.parametrize('path', ['/auth/login', '/auth/register', '/auth/logout', '/dashboard',
                                 '/checklist/1', '/reminders/new', '/questions/new',
                                 '/reminders/1/edit', '/questions/1/edit',
                                 '/reminders/1/delete', '/questions/1/delete'])
def test_csrf_missing_and_forged(client, path):
    assert client.post(path).status_code == 400
    assert client.post(path, data={'csrf_token': 'forged'}).status_code == 400


def test_logout_is_post_only_and_no_open_redirect(client):
    register(client)
    csrf = token(client, '/auth/login')
    response = client.post('/auth/login?next=https://example.org', data={
        'email': 'parent@example.com', 'password': 'a secure parent password', 'csrf_token': csrf})
    assert response.location.endswith('/dashboard')
    assert client.get('/auth/logout').status_code == 405


def test_session_cookie_tampering(client):
    client.set_cookie('session', 'forged-session')
    assert client.get('/dashboard').status_code == 302
