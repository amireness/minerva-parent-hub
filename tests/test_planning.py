from datetime import date

import pytest

from parenthub import create_app
from parenthub.extensions import db
from parenthub.models import ParentQuestion, Reminder, UserChecklistProgress
from conftest import login, post, register


def test_complete_persistent_flow(app, parent):
    assert post(parent, '/planning', {'age_group': 'under18'}).status_code == 302
    assert 'Published requirement' in parent.get('/planning').text
    assert post(parent, '/checklist/1', {'completed': 'y'}, source='/checklist').status_code == 302
    assert '1 of 5' in parent.get('/planning').text
    assert post(parent, '/reminders/new', {'title': 'Call Admissions', 'due_date': '2027-01-02'}).status_code == 302
    assert post(parent, '/reminders/1/edit', {'title': 'Review deadlines', 'due_date': '2027-01-03'}).status_code == 302
    assert post(parent, '/questions/new', {'body': 'Which parent steps apply?'}).status_code == 302
    assert post(parent, '/questions/1/edit', {'body': 'What permission is required?', 'resolved': 'y'}).status_code == 302
    post(parent, '/auth/logout', source='/planning')

    # A second factory and client read the same on-disk database with a new session.
    reopened = create_app({'TESTING': True, 'SECRET_KEY': 'test-only-secret',
                           'SQLALCHEMY_DATABASE_URI': app.config['SQLALCHEMY_DATABASE_URI']})
    returning = reopened.test_client()
    assert login(returning).status_code == 302
    dashboard = returning.get('/planning').text
    assert 'Published requirement' in dashboard
    assert '1 of 5' in dashboard
    assert 'Review deadlines' in dashboard
    assert '2027-01-03' in returning.get('/reminders').text
    assert 'What permission is required?' in returning.get('/questions').text
    with reopened.app_context():
        assert db.session.get(ParentQuestion, 1).resolved
        db.session.remove()
        db.engine.dispose()


def test_checklist_toggle_and_unique_progress(app, parent):
    for _ in range(2):
        assert post(parent, '/checklist/1', {'completed': 'y'}, source='/checklist').status_code == 302
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(UserChecklistProgress)) == 1
    assert post(parent, '/checklist/1', source='/checklist').status_code == 302
    assert '0 of 5' in parent.get('/planning').text
    assert post(parent, '/checklist/999', source='/checklist').status_code == 404


def test_age_validation(parent):
    assert post(parent, '/planning', {'age_group': 'invented'}).status_code == 422
    assert post(parent, '/planning', {'age_group': 'adult'}).status_code == 302
    text = parent.get('/planning').text
    assert '18 or older' in text
    assert 'This guide has not verified parent access rights.' in text
    assert 'Published requirement' not in text


@pytest.mark.parametrize('path,data', [
    ('/reminders/new', {'title': ' ', 'due_date': '2027-01-01'}),
    ('/reminders/new', {'title': 'Test', 'due_date': 'not-a-date'}),
    ('/reminders/new', {'title': 'Test', 'due_date': '2027-02-30'}),
    ('/reminders/new', {'title': 'x' * 161, 'due_date': '2027-01-01'}),
    ('/questions/new', {'body': ' '}),
    ('/questions/new', {'body': 'x' * 1001}),
])
def test_invalid_inputs_do_not_write(app, parent, path, data):
    assert post(parent, path, data).status_code == 422
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Reminder)) == 0
        assert db.session.scalar(db.select(db.func.count()).select_from(ParentQuestion)) == 0


def test_completion_reopen_delete(app, parent):
    post(parent, '/reminders/new', {'title': 'My task', 'due_date': '2027-01-01'})
    post(parent, '/reminders/1/edit', {'title': 'My task', 'due_date': '2027-01-01', 'completed': 'y'})
    assert 'My task' not in parent.get('/planning').text
    assert 'My task' in parent.get('/reminders').text
    with app.app_context():
        reminder = db.session.get(Reminder, 1)
        assert reminder.completed and reminder.due_date == date(2027, 1, 1)
    post(parent, '/reminders/1/edit', {'title': 'My task', 'due_date': '2027-01-01'})
    assert 'My task' in parent.get('/planning').text
    post(parent, '/questions/new', {'body': 'Private question'})
    assert post(parent, '/reminders/1/delete', source='/reminders').status_code == 302
    assert post(parent, '/questions/1/delete', source='/questions').status_code == 302
    with app.app_context():
        assert db.session.get(Reminder, 1) is None
        assert db.session.get(ParentQuestion, 1) is None


def test_other_account_cannot_read_edit_or_delete(app, parent):
    post(parent, '/reminders/new', {'title': 'Secret reminder', 'due_date': '2027-01-01'})
    post(parent, '/questions/new', {'body': 'Secret question'})
    post(parent, '/checklist/1', {'completed': 'y'}, source='/checklist')
    other = app.test_client()
    register(other, 'other@example.com')
    login(other, 'other@example.com')
    assert 'Secret reminder' not in other.get('/reminders').text
    assert 'Secret reminder' not in other.get('/planning').text
    assert 'Secret question' not in other.get('/questions').text
    assert '0 of 5' in other.get('/planning').text
    for kind in ('reminders', 'questions'):
        assert other.get(f'/{kind}/1/edit').status_code == 404
        for action in ('edit', 'delete'):
            response = post(other, f'/{kind}/1/{action}', {'title': 'Hacked', 'body': 'Hacked',
                                                         'due_date': '2028-01-01'}, source=f'/{kind}')
            assert response.status_code == 404
    post(other, '/checklist/1', source='/checklist')
    with app.app_context():
        assert db.session.get(Reminder, 1).title == 'Secret reminder'
        assert db.session.get(ParentQuestion, 1).body == 'Secret question'
    assert '1 of 5' in parent.get('/planning').text


def test_escape_untrusted_text_and_ignore_owner_input(app, parent):
    payload = '<script>alert(1)</script>'
    response = post(parent, '/questions/new', {'body': payload, 'user_id': 999}, follow_redirects=True)
    assert response.status_code == 200
    assert payload not in response.text
    assert '&lt;script&gt;' in response.text
    with app.app_context():
        assert db.session.get(ParentQuestion, 1).user_id == 1


def test_invalid_edit_preserves_record(app, parent):
    post(parent, '/reminders/new', {'title': 'Keep me', 'due_date': '2027-01-01'})
    assert post(parent, '/reminders/1/edit', {'title': 'Changed', 'due_date': 'bad'}).status_code == 422
    with app.app_context():
        assert db.session.get(Reminder, 1).title == 'Keep me'
