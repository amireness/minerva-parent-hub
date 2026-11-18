import re
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import inspect

from conftest import login, post, register
from parenthub.extensions import db
from parenthub.models import ParentInvitation, SyntheticApplicant, SyntheticMilestone, User


@pytest.fixture
def invite(app):
    def create(email='parent@example.com', number='SYN-FIRST', code='first-invite'):
        with app.app_context():
            applicant = SyntheticApplicant(application_number=number, milestones=[
                SyntheticMilestone(position=1, title=f'Milestone for {number}', completed=True),
            ])
            db.session.add(applicant)
            db.session.flush()
            today = datetime.now(timezone.utc).date()
            invitation = ParentInvitation(applicant_id=applicant.id, invited_email=email,
                                          code_digest=ParentInvitation.digest_code(code),
                                          expires_on=today + timedelta(days=7))
            db.session.add(invitation)
            db.session.commit()
            return invitation.id
    return create


def test_pending_invitation_does_not_unlock_dashboard(app, parent, invite):
    invitation_id = invite()
    response = parent.get('/dashboard?application_number=SYN-FIRST')
    assert 'Invitation required' in response.text
    assert 'SYN-FIRST' not in response.text
    assert parent.post('/dashboard', data={'code': 'first-invite'}).status_code == 400
    assert post(parent, '/dashboard', {'code': 'SYN-FIRST'}).status_code == 422
    assert post(parent, '/dashboard', {'code': 'first-invite'}, follow_redirects=True).status_code == 200
    assert 'Milestone for SYN-FIRST' in parent.get('/dashboard').text
    assert post(parent, '/dashboard', {'code': 'first-invite'}).status_code == 422
    with app.app_context():
        invitation = db.session.get(ParentInvitation, invitation_id)
        assert invitation.accepted_by_id == db.session.scalar(db.select(User.id))
        assert invitation.accepted_on is not None
    post(parent, '/auth/logout', source='/dashboard')
    assert parent.get('/dashboard').status_code == 302
    assert login(parent).status_code == 302
    assert 'Milestone for SYN-FIRST' in parent.get('/dashboard').text


def test_account_isolation_and_email_binding(app, parent, invite):
    invite()
    invite('other@example.com', 'SYN-SECOND', 'second-invite')
    other = app.test_client()
    assert register(other, 'other@example.com').status_code == 302
    assert login(other, 'other@example.com').status_code == 302
    assert post(other, '/dashboard', {'code': 'first-invite'}).status_code == 422
    assert post(parent, '/dashboard', {'code': 'first-invite'}).status_code == 302
    assert post(other, '/dashboard', {'code': 'second-invite'}).status_code == 302
    for account, own, foreign in [(parent, 'SYN-FIRST', 'SYN-SECOND'), (other, 'SYN-SECOND', 'SYN-FIRST')]:
        response = account.get(f'/dashboard?application_number={foreign}')
        assert f'Milestone for {own}' in response.text
        assert foreign not in response.text
        assert foreign not in account.get('/planning').text


@pytest.mark.parametrize('field', ['expires_on', 'revoked_on'])
@pytest.mark.parametrize('accept_first', [False, True])
def test_expired_and_revoked_invitations_are_invalid(app, parent, invite, field, accept_first):
    invitation_id = invite()
    if accept_first:
        assert post(parent, '/dashboard', {'code': 'first-invite'}).status_code == 302
    with app.app_context():
        invitation = db.session.get(ParentInvitation, invitation_id)
        setattr(invitation, field, datetime.now(timezone.utc).date())
        db.session.commit()
    assert post(parent, '/dashboard', {'code': 'first-invite'}).status_code == 422
    response = parent.get('/dashboard')
    assert 'Invitation required' in response.text
    assert 'SYN-FIRST' not in response.text


def test_public_pages_and_uninvited_planning(client):
    for path in ('/guide', '/resources', '/deadlines', '/financial-aid'):
        assert client.get(path).status_code == 200
    assert client.get('/planning').status_code == 302
    assert register(client).status_code == 302
    assert login(client).status_code == 302
    assert 'Invitation required' in client.get('/dashboard').text
    assert 'Your checklist' in client.get('/planning').text


def test_dev_seed_and_additive_schema(app, parent):
    # Model a pre-onboarding database while preserving the existing parent account.
    with app.app_context():
        for model in (ParentInvitation, SyntheticMilestone, SyntheticApplicant):
            model.__table__.drop(db.engine)
    runner = app.test_cli_runner()
    assert runner.invoke(args=['init-db']).exit_code == 0
    with app.app_context():
        assert inspect(db.engine).has_table('parent_invitation')
        assert db.session.scalar(db.select(User.email)) == 'parent@example.com'
    args = ['seed-invitations', '--email', 'PARENT@example.com', '--count', '2']
    assert runner.invoke(args=args).exit_code == 1
    result = runner.invoke(args=args, env={'FLASK_DEBUG': '1'})
    assert result.exit_code == 0, result.output
    entries = re.findall(r'(SYN-[0-9A-F]+) invitation code: ([\w-]+)', result.output)
    assert len(entries) == 2 and entries[0] != entries[1]
    for _, code in entries:
        assert post(parent, '/dashboard', {'code': code}).status_code == 302
    dashboard = parent.get('/dashboard').text
    for number, code in entries:
        assert number in dashboard and code not in dashboard
    with app.app_context():
        invitations = db.session.scalars(db.select(ParentInvitation)).all()
        assert {row.code_digest for row in invitations} == {
            ParentInvitation.digest_code(code) for _, code in entries
        }
