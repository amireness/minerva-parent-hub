from conftest import login, post, register
from parenthub.aid_guidance import STEP_PREFIX
from parenthub.extensions import db
from parenthub.models import ChecklistItem


def test_public_preparation_has_connected_guides_and_no_upload(client):
    page = client.get('/financial-aid')
    assert page.status_code == 200
    assert 'Understand financial aid' in page.text and 'type="file"' not in page.text
    assert 'Example amount' not in page.text and 'Fictional original excerpt' not in page.text
    for view, text in [('glossary', 'id="term-income"'), ('translations', 'Fictional original excerpt'),
                       ('currency', 'Illustrative rates authored'), ('process', 'Financial Aid Questionnaire')]:
        assert text in client.get('/financial-aid?view=' + view).text
    step = client.get('/financial-aid?view=step&step=records').text
    assert 'step=translations' in step and 'step=dates' in step
    assert 'view=glossary' in step and 'return_step=records' in step
    assert 'step-submission' not in step and 'Mark prepared' not in step
    assert 'aria-current="step"' in step and '>Documents</span>' in step
    assert 'Save and next' not in step and 'Not prepared' not in step
    assert 'to save your checklist' not in step and 'Log in to save progress' in page.text
    tool = client.get('/financial-aid?view=glossary&return_step=records&term=income').text
    assert 'Back to preparation step' in tool and 'step=records' in tool
    assert 'id="term-income"' in tool and ' open>' in tool


def test_learning_journey_explains_aid_before_preparation(parent):
    topics = [
        ('understand', 'Financial aid helps students', 'process'),
        ('process', 'Tax returns are one part', 'role'),
        ('role', 'The student keeps control', 'forms'),
        ('forms', 'https://www.minerva.edu/financial-aid-center/', 'offer'),
        ('offer', 'Expected family contribution', None),
    ]
    for key, content, following in topics:
        page = parent.get('/financial-aid?view=learn&topic=' + key)
        assert page.status_code == 200
        assert content in page.text and 'Save and next' not in page.text
        expected = f'topic={following}">Next' if following else 'view=step">Go to preparation'
        assert expected in page.text
    assert parent.get('/financial-aid?view=learn&topic=invalid').status_code == 404
    assert '0 of 7 prepared' in parent.get('/financial-aid?view=review').text


def test_guided_checklist_uses_existing_private_progress(app, parent):
    with app.app_context():
        item_id = db.session.scalar(db.select(ChecklistItem.id).where(ChecklistItem.slug == STEP_PREFIX + 'start'))
    response = post(parent, f'/checklist/{item_id}', {'completed': 'y', 'advance': '1'},
                    source='/financial-aid?view=step&step=start')
    assert response.location.endswith('/financial-aid?view=step&step=forms')
    page = parent.get('/financial-aid?view=review').text
    assert 'step=forms">Continue preparation' in page
    assert '1 of 7 prepared' in page
    step = parent.get('/financial-aid?view=step&step=forms').text
    assert 'data-prepared' in step and 'class="sr-only">Prepared' in step
    assert 'Save and next' in step
    assert '0 of 5' in parent.get('/planning').text
    assert '/checklist/' + str(item_id) not in parent.get('/checklist').text
    other = app.test_client()
    register(other, 'other@example.com')
    login(other, 'other@example.com')
    assert 'step=start">Start preparation' in other.get('/financial-aid?view=review').text
    post(parent, f'/checklist/{item_id}', source='/financial-aid?view=step&step=start')
    assert '0 of 7 prepared' in parent.get('/financial-aid?view=review').text
