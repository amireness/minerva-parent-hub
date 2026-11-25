from conftest import login, post, register
from parenthub.aid_guidance import STEP_PREFIX
from parenthub.extensions import db
from parenthub.models import ChecklistItem


def test_public_preparation_has_connected_guides_and_no_upload(client):
    page = client.get('/financial-aid')
    assert page.status_code == 200
    assert 'Start preparation' in page.text and 'type="file"' not in page.text
    assert 'Example amount' not in page.text and 'Fictional original excerpt' not in page.text
    for view, text in [('glossary', 'id="term-income"'), ('translations', 'Fictional original excerpt'),
                       ('currency', 'Illustrative rates authored'), ('process', 'Financial Aid Questionnaire')]:
        assert text in client.get('/financial-aid?view=' + view).text
    step = client.get('/financial-aid?view=step&step=records').text
    assert 'step=translations' in step and 'step=dates' in step
    assert 'view=glossary' in step and 'return_step=records' in step
    assert 'step-submission' not in step and 'Mark prepared' not in step
    tool = client.get('/financial-aid?view=glossary&return_step=records&term=income').text
    assert 'Back to preparation step' in tool and 'step=records' in tool
    assert 'id="term-income"' in tool and ' open>' in tool


def test_guided_checklist_uses_existing_private_progress(app, parent):
    with app.app_context():
        item_id = db.session.scalar(db.select(ChecklistItem.id).where(ChecklistItem.slug == STEP_PREFIX + 'start'))
    response = post(parent, f'/checklist/{item_id}', {'completed': 'y', 'advance': '1'},
                    source='/financial-aid?view=step&step=start')
    assert response.location.endswith('/financial-aid?view=step&step=forms')
    page = parent.get('/financial-aid?view=review').text
    assert 'step=forms">Continue preparation' in page
    assert '1 of 7 prepared' in page
    assert '0 of 5' in parent.get('/planning').text
    assert '/checklist/' + str(item_id) not in parent.get('/checklist').text
    other = app.test_client()
    register(other, 'other@example.com')
    login(other, 'other@example.com')
    assert 'step=start">Start preparation' in other.get('/financial-aid?view=review').text
    post(parent, f'/checklist/{item_id}', source='/financial-aid?view=step&step=start')
    assert '0 of 7 prepared' in parent.get('/financial-aid?view=review').text
