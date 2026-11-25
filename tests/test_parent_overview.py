import re

import pytest

from conftest import post
from parenthub.extensions import db
from parenthub.models import SyntheticMilestone


@pytest.mark.parametrize('path', ['/account', '/aid-preparation', '/application-progress'])
def test_signed_in_sections_require_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_account_preserves_invitation_flow(app, parent):
    runner = app.test_cli_runner()
    seeded = runner.invoke(
        args=['seed-invitations', '--email', 'parent@example.com'],
        env={'FLASK_DEBUG': '1'},
    )
    assert seeded.exit_code == 0
    code = re.search(r'invitation code: (\S+)', seeded.output).group(1)
    assert post(parent, '/dashboard', {'code': code}, source='/account').status_code == 302
    response = parent.get('/dashboard')
    assert 'Application submitted' in response.text
    assert re.search(r'aria-current="step">\s*<strong>Application started</strong>', response.text)
    assert 'What you can do now' in response.text and 'Review financial aid documents' in response.text
    progress = parent.get('/application-progress')
    assert '<strong>Application started</strong>' in progress.text
    assert '<strong>Application submitted</strong>' in progress.text
    assert 'aria-current="step"' in progress.text and '<details open>' in progress.text
    assert 'Your applicant has begun working on the application.' in progress.text
    assert 'Decision available' in progress.text
    assert 'Accept invitation' not in response.text
    assert '/account' in response.text
    rejected = post(parent, '/dashboard', {'code': code}, source='/account')
    assert rejected.status_code == 422 and 'Applicant invitations' in rejected.text

    with app.app_context():
        db.session.execute(db.update(SyntheticMilestone).values(completed=True))
        db.session.commit()
    response = parent.get('/dashboard')
    assert '<dd>Decision available</dd>' in response.text
    assert 'No further demo milestones' in response.text

    with app.app_context():
        db.session.execute(db.update(SyntheticMilestone).values(completed=False))
        db.session.commit()
    response = parent.get('/dashboard')
    assert 'Before first milestone' in response.text
    assert '<dd>Application started</dd>' in response.text
    assert 'aria-current="step"' not in response.text

    with app.app_context():
        db.session.execute(db.delete(SyntheticMilestone))
        db.session.commit()
    assert 'No milestones available' in parent.get('/dashboard').text


def test_aid_examples_are_scoped_and_read_only(parent):
    response = parent.get('/aid-preparation', follow_redirects=True)
    assert response.status_code == 200
    assert 'Start preparation' in response.text
    response = parent.get('/financial-aid?view=documents')
    assert response.text.count('<details class="aid-category-details"') == 4
    for text in ('returning-student guidance', 'Confirm first-year requirements',
                 'How to help', 'past two years',
                 'most recent three months', 'most recent twelve months', 'businesses, farms',
                 '/reminders/new', '/questions/new', '/financial-aid'):
        assert text in response.text
    assert 'type="file"' not in response.text
    assert 'Preparation status' not in response.text
    assert 'Location note' not in response.text
    assert parent.get('/financial-aid').status_code == 200
