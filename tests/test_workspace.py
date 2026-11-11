import re

from parenthub.extensions import db
from parenthub.models import ChecklistItem, Resource
from conftest import login, post, register


def test_public_home_explains_app_and_has_working_actions(client):
    response = client.get('/')
    assert response.status_code == 200
    for text in ['verified official resources', 'Get started', 'Explore official resources',
                 'Your checklist', 'Personal reminders', 'Questions for Admissions',
                 'A companion to Minerva', 'Independent prototype']:
        assert text in response.text
    assert '/auth/register' in response.text
    assert '/resources' in response.text
    assert '<iframe' not in response.text


def test_signed_in_home_remains_workspace(parent):
    assert parent.get('/').location.endswith('/dashboard')
    text = parent.get('/dashboard').text
    assert 'parent@example.com' in text
    assert 'value="0" max="5"' in text
    assert 'Set your family context' in text
    assert 'Get started' not in text


def test_next_action_uses_only_own_incomplete_parent_items(app, parent):
    post(parent, '/dashboard', {'age_group': 'adult'})
    assert '/checklist#item-1' in parent.get('/dashboard').text
    other = app.test_client()
    register(other, 'another@example.com')
    login(other, 'another@example.com')
    post(other, '/checklist/1', {'completed': 'y'}, source='/checklist')
    assert '/checklist#item-1' in parent.get('/dashboard').text
    post(parent, '/checklist/1', {'completed': 'y'}, source='/checklist')
    assert '/checklist#item-2' in parent.get('/dashboard').text
    post(parent, '/checklist/2', {'completed': 'y'}, source='/checklist')
    text = parent.get('/dashboard').text
    assert 'Review your questions' in text
    assert '/checklist#item-3' not in text


def test_question_preview_is_owned_open_and_links_to_edit(app, parent):
    post(parent, '/questions/new', {'body': 'My open planning question'})
    other = app.test_client()
    register(other, 'another@example.com')
    login(other, 'another@example.com')
    post(other, '/questions/new', {'body': 'Someone else private question'})
    text = parent.get('/dashboard').text
    assert 'My open planning question' in text and '/questions/1/edit' in text
    assert 'Someone else private question' not in text
    post(parent, '/questions/1/edit', {'body': 'My open planning question', 'resolved': 'y'})
    assert 'My open planning question' not in parent.get('/dashboard').text


def test_empty_checklist_progress_does_not_divide_by_zero(app, parent):
    with app.app_context():
        for item in db.session.scalars(db.select(ChecklistItem)).all():
            db.session.delete(item)
        db.session.commit()
    response = parent.get('/dashboard')
    assert response.status_code == 200
    assert 'value="0" max="1"' in response.text
    assert '0 of 0 planning items' in response.text


def test_guidance_sections_and_source_links(client):
    text = client.get('/guide').text
    for anchor in ['application', 'parent-involvement', 'aid-preparation', 'planning', 'support']:
        assert f'href="#{anchor}"' in text and f'id="{anchor}"' in text
    for source in ['https://www.minerva.edu/undergraduate/admissions/',
                   'https://www.minerva.edu/parents-families/',
                   'https://www.minerva.edu/undergraduate/financial-aid/']:
        assert source in text
    assert 'Applicant responsibilities' in text
    assert 'Parent planning' in text


def test_new_resources_keep_provenance_and_search(client, app):
    text = client.get('/resources?topic=Planning+ahead').text
    assert 'https://www.minerva.edu/academic-calendar/' in text
    assert 'not an admissions deadline schedule' in text
    assert 'Last verified 2026-11-11' in text
    assert 'Understanding Minerva' in client.get('/resources?q=discussion').text
    with app.app_context():
        resources = db.session.scalars(db.select(Resource)).all()
        assert all(resource.url.startswith('https://www.minerva.edu/') for resource in resources)


def test_form_errors_identify_fields_and_success_is_announced(parent):
    response = post(parent, '/reminders/new', {'title': 'Follow up', 'due_date': 'bad-date'})
    assert response.status_code == 422
    assert 'aria-invalid="true"' in response.text
    assert 'id="due_date-errors"' in response.text
    saved = post(parent, '/reminders/new', {'title': 'Follow up', 'due_date': '2027-01-05'}, follow_redirects=True)
    assert re.search(r'role="status"[^>]*>Reminder saved\.', saved.text)
