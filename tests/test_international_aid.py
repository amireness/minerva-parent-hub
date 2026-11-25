from conftest import login, post, register
from parenthub.aid_guidance import STEP_PREFIX
from parenthub.extensions import db
from parenthub.models import ChecklistItem


def test_public_preparation_has_connected_guides_and_no_upload(client):
    page = client.get('/financial-aid')
    assert page.status_code == 200
    for text in ('Financial aid glossary', 'Fictional original excerpt', 'Illustrative English translation',
                 'Illustrative rates authored', 'First-time financial aid checklist', 'CSS Profile',
                 'Financial Aid Questionnaire', 'Retirement contribution'):
        assert text in page.text
    assert 'href="#term-income"' in page.text and 'id="term-income"' in page.text
    assert 'id="completed-start"' not in page.text
    assert 'type="file"' not in page.text


def test_guided_checklist_uses_existing_private_progress(app, parent):
    with app.app_context():
        item_id = db.session.scalar(db.select(ChecklistItem.id).where(ChecklistItem.slug == STEP_PREFIX + 'start'))
    response = post(parent, f'/checklist/{item_id}', {'completed': 'y'}, source='/financial-aid')
    assert response.location.endswith('/financial-aid#step-start')
    page = parent.get('/financial-aid').text
    assert '<a href="#step-forms">Next in your plan</a>' in page
    assert 'name="completed" checked' in page
    assert '0 of 5' in parent.get('/planning').text
    assert '/checklist/' + str(item_id) not in parent.get('/checklist').text
    other = app.test_client()
    register(other, 'other@example.com')
    login(other, 'other@example.com')
    assert '<a href="#step-start">Next in your plan</a>' in other.get('/financial-aid').text
