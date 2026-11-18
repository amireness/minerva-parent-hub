from datetime import datetime, timedelta, timezone

from conftest import post
from parenthub.extensions import db
from parenthub.models import SyntheticApplicantRound


def test_unconfirmed_deadlines_have_source_and_no_calendar(client):
    for path in ('/', '/deadlines'):
        page = client.get(path).text
        assert 'No upcoming deadline with a verified cutoff.' in page
        assert 'https://www.minerva.edu/undergraduate/admissions/' in page
        assert 'Add to Calendar' not in page
    assert client.get('/deadlines/unconfirmed.ics').status_code == 404


def test_calendar_uses_verified_instant_and_rejects_expired_or_incomplete(app, client):
    now = datetime.now(timezone.utc)
    target = (now + timedelta(days=2)).astimezone(timezone(timedelta(hours=-8))).replace(microsecond=0)
    event = {'slug': 'verified-test', 'title': 'Test deadline, admissions', 'at': target.isoformat(),
             'source': 'https://www.minerva.edu/undergraduate/admissions/',
             'verified_on': now.date().isoformat()}
    app.config['EXACT_DEADLINES'] = [
        event, dict(event, slug='expired', at=(now - timedelta(days=1)).isoformat()),
        dict(event, slug='missing-zone', at=target.replace(tzinfo=None).isoformat()),
        dict(event, slug='wrong-source', source='https://example.org/'),
    ]
    for path in ('/', '/deadlines'):
        page = client.get(path).text
        assert 'UTC-08:00' in page
        assert 'data-deadline=' in page and 'Due soon' in page
        assert '/deadlines/verified-test.ics' in page
        assert '/deadlines/expired.ics' not in page
    response = client.get('/deadlines/verified-test.ics')
    assert response.status_code == 200
    assert response.mimetype == 'text/calendar'
    assert response.headers['Content-Disposition'] == 'attachment; filename="verified-test.ics"'
    assert b'BEGIN:VCALENDAR\r\n' in response.data
    assert b'SUMMARY:Test deadline\\, admissions\r\n' in response.data
    utc = target.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    assert f'DTSTART:{utc}\r\n'.encode() in response.data
    assert all(len(line) <= 75 for line in response.data.split(b'\r\n'))
    for slug in ('expired', 'missing-zone', 'wrong-source'):
        assert client.get(f'/deadlines/{slug}.ics').status_code == 404


def test_parent_home_favors_only_linked_applicant_round(app, parent):
    now = datetime.now(timezone.utc)
    fixture = {'source': 'https://www.minerva.edu/undergraduate/admissions/',
               'verified_on': now.date().isoformat()}
    app.config['EXACT_DEADLINES'] = [
        dict(fixture, slug='general', title='General deadline', at=(now + timedelta(days=1)).isoformat()),
        dict(fixture, slug='early', title='Early round deadline', round_slug='early-action',
             at=(now + timedelta(days=2)).isoformat()),
        dict(fixture, slug='regular', title='Regular round deadline', round_slug='regular-one',
             at=(now + timedelta(days=3)).isoformat()),
    ]
    result = app.test_cli_runner().invoke(
        args=['seed-invitations', '--email', 'parent@example.com'], env={'FLASK_DEBUG': '1'},
    )
    assert result.exit_code == 0
    code = result.output.split('invitation code: ')[1].strip()
    assert post(parent, '/dashboard', {'code': code}).status_code == 302
    assert 'General deadline' in parent.get('/dashboard').text
    with app.app_context():
        db.session.add(SyntheticApplicantRound(applicant_id=1, round_slug='regular-one'))
        db.session.commit()
    page = parent.get('/dashboard').text
    assert 'Regular round deadline' in page and 'Early round deadline' not in page
    assert 'General deadline' in app.test_client().get('/').text


def test_help_is_public_and_separates_contact_from_saved_questions(client, parent):
    guest = client.application.test_client()
    for session in (guest, parent):
        for path in ('/help', '/guide', '/deadlines', '/financial-aid'):
            page = session.get(path)
            assert page.status_code == 200
            assert 'class="help-nav" href="/help"' in page.text
        page = session.get('/help').text
        assert 'mailto:admissions@minerva.edu' in page
        assert 'mailto:newstudentaid@minerva.edu' in page
        assert 'href="/questions"' in page
        assert 'https://www.minerva.edu/faqs/" target="_blank" rel="noopener noreferrer"' in page
