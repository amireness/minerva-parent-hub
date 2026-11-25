import re
from datetime import datetime, timezone

import pytest

from conftest import login, post, register
from parenthub.extensions import db
from parenthub.models import AidDocument, AidPreparation, ParentInvitation, SyntheticStudent


def seed(app, command, *args):
    return app.test_cli_runner().invoke(args=[command, *args], env={'FLASK_DEBUG': '1'})


def invite(app, client, email):
    result = seed(app, 'seed-invitations', '--email', email)
    assert result.exit_code == 0, result.output
    number, code = re.search(r'(SYN-\w+) invitation code: (\S+)', result.output).groups()
    assert post(client, '/dashboard', {'code': code}).status_code == 302
    return number


def document_action(client, applicant=1, category='income-tax', action='link', sample='1'):
    data = {'sample': sample} if action == 'link' else {}
    return post(client, f'/financial-aid/{applicant}/{category}/{action}', data, source='/financial-aid')


def student_login(app, number, email):
    result = seed(app, 'seed-student', '--email', email, '--application-number', number)
    assert result.exit_code == 0, result.output
    password = re.search(r'Generated password \(shown once\): (\S+)', result.output).group(1)
    client = app.test_client()
    assert post(client, '/auth/login', {'email': email, 'password': password}).status_code == 302
    assert client.get('/dashboard').location.endswith('/student/preparation')
    return client


def test_document_lifecycle_drives_progress_and_persists(app, parent):
    invite(app, parent, 'parent@example.com')
    assert '0 of 4 documents added' in parent.get('/financial-aid?view=documents').text
    chooser = parent.get('/financial-aid?category=income-tax').text
    assert 'Google Drive example' in chooser and 'https://drive.example.com/income-tax/1' in chooser
    assert document_action(parent).status_code == 302
    assert 'Review linked documents' in parent.get('/dashboard').text
    assert post(parent, '/auth/logout', source='/financial-aid').status_code == 302
    assert login(parent).status_code == 302
    page = parent.get('/financial-aid?view=documents').text
    assert '1 of 4 documents added' in page and 'Tax-record-example-1.pdf' in page
    assert 'Shared with student' not in page and 'type="file"' not in page
    assert 'Fictional file preview' in parent.get('/financial-aid/1/income-tax/open').text
    assert document_action(parent, sample='2').status_code == 302
    page = parent.get('/financial-aid?view=documents').text
    assert '1 of 4 documents added' in page and 'Tax-record-example-2.pdf' in page
    assert document_action(parent, action='remove').status_code == 302
    assert '0 of 4 documents added' in parent.get('/financial-aid?view=documents').text
    assert parent.get('/financial-aid/1/income-tax/open').status_code == 404
    assert parent.get('/application-progress').text.count('aria-current="step"') == 1


def test_writes_and_previews_require_ownership_and_fixed_sample(app, parent):
    invite(app, parent, 'parent@example.com')
    other = app.test_client()
    assert register(other, 'other@example.com').status_code == 302
    assert login(other, 'other@example.com').status_code == 302
    invite(app, other, 'other@example.com')
    assert document_action(parent).status_code == 302
    assert document_action(other).status_code == 404
    assert other.get('/financial-aid/1/income-tax/open').status_code == 404
    assert other.get('/financial-aid?applicant=1').status_code == 404
    assert '0 of 4 documents added' in other.get('/financial-aid?view=documents').text
    rejected = document_action(parent, sample='https://drive.google.com/file/d/example')
    assert rejected.status_code == 422 and 'drive.google.com' not in rejected.text
    assert document_action(parent, sample='99').status_code == 422
    assert parent.post('/financial-aid/1/income-tax/link').status_code == 400
    with app.app_context():
        row = db.session.get(AidDocument, (1, 1, 'income-tax'))
        assert (row.sample, row.shared) == (1, False)


def test_student_only_sees_shared_presence_for_their_applicant(app, parent):
    number = invite(app, parent, 'parent@example.com')
    student = student_login(app, number, 'student@example.com')
    other_parent = app.test_client()
    assert register(other_parent, 'other@example.com').status_code == 302
    assert login(other_parent, 'other@example.com').status_code == 302
    other_number = invite(app, other_parent, 'other@example.com')
    other_student = student_login(app, other_number, 'other-student@example.com')

    assert document_action(parent, action='share').status_code == 404
    assert document_action(parent).status_code == 302
    assert document_action(parent, action='share').status_code == 302
    assert 'Shared with student' in parent.get('/financial-aid?view=documents').text
    assert document_action(parent, category='bank').status_code == 302
    assert document_action(other_parent, applicant=2, category='assets').status_code == 302
    assert document_action(other_parent, applicant=2, category='assets', action='share').status_code == 302
    assert parent.get('/student/preparation').status_code == 404
    assert student.get('/financial-aid?applicant=1').status_code == 404
    assert student.get('/financial-aid/1/income-tax/open').status_code == 404
    assert document_action(student).status_code == 404
    page = student.get('/student/preparation?applicant=2').text
    assert 'Income and tax records' in page and 'Example document added' in page
    assert 'Tax-record-example-1.pdf' not in page
    assert 'Bank statements' not in page and 'Property, businesses' not in page
    assert 'Income and tax records' not in other_student.get('/student/preparation').text
    assert 'Property, businesses' in other_student.get('/student/preparation').text

    assert document_action(parent, action='unshare').status_code == 302
    assert 'Income and tax records' not in student.get('/student/preparation').text
    assert document_action(parent, action='share').status_code == 302
    assert document_action(parent, sample='2').status_code == 302
    assert 'Income and tax records' not in student.get('/student/preparation').text
    assert document_action(parent, action='share').status_code == 302
    with app.app_context():
        invitation = db.session.get(ParentInvitation, 1)
        invitation.revoked_on = datetime.now(timezone.utc).date()
        db.session.commit()
    assert 'Income and tax records' not in student.get('/student/preparation').text
    assert document_action(parent).status_code == 404
    assert parent.get('/application-progress').location.endswith('/dashboard')


@pytest.mark.parametrize('path', ['/application-progress', '/student/preparation'])
def test_private_routes_require_login(client, path):
    assert '/auth/login' in client.get(path).location


def test_student_provisioning_cannot_reuse_an_account(app, parent):
    number = invite(app, parent, 'parent@example.com')
    args = ['seed-student', '--email', 'student@example.com', '--application-number', number]
    assert app.test_cli_runner().invoke(args=args, env={'FLASK_DEBUG': '0'}).exit_code == 1
    assert seed(app, 'seed-student', '--email', 'parent@example.com', '--application-number', number).exit_code == 1
    student_login(app, number, 'student@example.com')
    assert seed(app, 'seed-student', '--email', 'second@example.com', '--application-number', number).exit_code == 1


def test_init_db_preserves_old_rows_without_turning_them_into_linked_files(app, parent):
    number = invite(app, parent, 'parent@example.com')
    with app.app_context():
        db.session.add(AidPreparation(parent_id=1, applicant_id=1, category='income-tax',
                                      status='ready', location='paper', shared=True))
        db.session.commit()
        AidDocument.__table__.drop(db.engine)
    assert app.test_cli_runner().invoke(args=['init-db']).exit_code == 0
    assert number in parent.get('/dashboard').text
    assert '0 of 4 documents added' in parent.get('/financial-aid?view=documents').text
    assert document_action(parent).status_code == 302
    with app.app_context():
        assert db.session.get(AidPreparation, (1, 1, 'income-tax')).shared
