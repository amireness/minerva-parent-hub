import re
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from parenthub import create_app
from parenthub.extensions import db
from parenthub.models import ChecklistItem, OfficialDeadline, ParentQuestion, Reminder, Resource, User, UserChecklistProgress


@pytest.mark.parametrize('path', ['/guide', '/financial-aid', '/resources', '/deadlines',
                                 '/shared-css/styles.css', '/shared-css/parent-guide.css', '/static/app.css'])
def test_public_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_search_filter_and_injection(client):
    result = client.get('/resources?q=challenges&topic=Admissions').text
    assert 'Official application process and deadlines' in result
    assert 'Official financial aid steps and deadlines</a>' not in result
    assert 'No matching resources' in client.get('/resources?q=nonexistent').text
    assert 'No matching resources' in client.get('/resources?q=%25').text
    assert 'No matching resources' in client.get('/resources?q=%27%20OR%201=1--').text
    assert 'Last verified 2026-11-11' in result


def test_deadlines_have_no_inferred_year(client):
    text = client.get('/deadlines').text
    for published in ['November 1', 'November 8', 'January 5', 'January 12', 'March 2', 'March 9']:
        assert published in text
    assert 'Official tables omit calendar years.' in text
    assert 'https://www.minerva.edu/undergraduate/admissions/' in text
    assert '2027-' not in text


def test_constraints_and_foreign_keys(app):
    with app.app_context():
        assert db.session.execute(db.text('PRAGMA foreign_keys')).scalar() == 1
        db.session.add(Reminder(user_id=999, title='Invalid owner', due_date=date.today()))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        user = User(email='unique@example.com', password_hash='test-only', age_group='adult')
        db.session.add(user)
        db.session.commit()
        db.session.add_all([UserChecklistProgress(user_id=user.id, item_id=1),
                            UserChecklistProgress(user_id=user.id, item_id=1)])
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        user.age_group = 'invalid'
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_cli_seeding_idempotent_and_preserves_data(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=['init-db']).exit_code == 0
    assert runner.invoke(args=['seed-content']).exit_code == 0
    result = runner.invoke(args=['seed-demo'])
    assert result.exit_code == 0, result.output
    password = re.search(r'shown once\): (\S+)', result.output).group(1)
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.email == 'demo@example.com'))
        assert user.check_password(password)
        user_id = user.id
    assert runner.invoke(args=['seed-content']).exit_code == 0
    assert runner.invoke(args=['init-db']).exit_code == 0
    duplicate = runner.invoke(args=['seed-demo'])
    assert duplicate.exit_code != 0
    assert 'not changed' in duplicate.output
    with app.app_context():
        assert db.session.get(User, user_id).check_password(password)
        for model, count in [(Resource, 6), (ChecklistItem, 5), (OfficialDeadline, 3), (User, 1),
                             (Reminder, 1), (ParentQuestion, 1), (UserChecklistProgress, 1)]:
            assert db.session.scalar(db.select(db.func.count()).select_from(model)) == count


def test_missing_secret_fails_clearly(monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        create_app({'SECRET_KEY': None})


def test_error_status_codes(client):
    assert client.get('/not-a-route').status_code == 404
    assert client.get('/shared-css/content.json').status_code == 404
    assert client.post('/auth/register', data={'email': 'x' * 40000}).status_code == 413


def test_database_failure_rolls_back_and_returns_503(client, monkeypatch):
    def fail(*args, **kwargs):
        raise OperationalError('query', {}, Exception('simulated database failure'))
    monkeypatch.setattr(db.session, 'scalars', fail)
    response = client.get('/resources')
    assert response.status_code == 503
    assert 'Changes were not saved' in response.text
    assert 'simulated database failure' not in response.text
