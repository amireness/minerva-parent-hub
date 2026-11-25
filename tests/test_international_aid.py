import pytest

from conftest import post
from parenthub.aid_guidance import STEP_PREFIX
from parenthub.extensions import db
from parenthub.models import ChecklistItem, UserChecklistProgress


def test_public_preparation_has_connected_guides_and_no_upload(client):
    page = client.get('/financial-aid')
    assert page.status_code == 200
    assert 'What is financial aid?' in page.text and 'type="file"' not in page.text
    assert 'New to financial aid?' not in page.text
    assert page.text.count('href="/financial-aid?view=learn&amp;topic=understand" aria-current="step"') == 2
    assert 'What is financial aid?' in client.get('/financial-aid?view=overview').text
    assert 'Example amount' not in page.text and 'Fictional original excerpt' not in page.text
    for view, text in [('glossary', 'id="term-income"'), ('translations', 'Fictional original excerpt'),
                       ('currency', 'Illustrative rates authored'), ('process', 'Financial Aid Questionnaire')]:
        assert text in client.get('/financial-aid?view=' + view).text
    tools = client.get('/financial-aid?view=tools').text
    assert tools.count('href="/financial-aid?view=tools" aria-current="step"') == 2
    for view in ('glossary', 'translations', 'currency', 'documents'):
        assert f'view={view}"' in tools
    assert 'Preparation checklist' not in page.text and 'Log in to save progress' not in page.text
    tool = client.get('/financial-aid?view=glossary&return_step=records&term=income').text
    assert 'Back to Useful Tools' in tool
    assert 'id="term-income"' in tool and ' open>' in tool


def test_learning_journey_explains_aid_before_preparation(parent):
    page = parent.get('/financial-aid')
    assert page.status_code == 200 and 'What is financial aid?' in page.text
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
        expected = f'topic={following}">Next' if following else 'view=tools">Useful Tools'
        assert expected in page.text
        assert 'Review checklist' not in page.text and 'Keep real financial details' not in page.text
        assert ('Official Minerva Financial Aid' in page.text) == (key == 'forms')
    assert parent.get('/financial-aid?view=learn&topic=invalid').status_code == 404


@pytest.mark.parametrize(('query', 'destination'), [
    ('view=step', '/financial-aid?view=learn&topic=understand'),
    ('view=step&step=forms', '/financial-aid?view=learn&topic=forms'),
    ('view=step&step=dates', '/deadlines'),
    ('view=step&step=records', '/financial-aid?view=documents'),
    ('view=step&step=translations', '/financial-aid?view=translations'),
    ('view=step&step=review', '/financial-aid?view=currency'),
    ('view=step&step=submission', '/financial-aid?view=learn&topic=forms'),
    ('view=review', '/financial-aid?view=tools'),
])
def test_retired_preparation_urls_redirect(client, query, destination):
    response = client.get('/financial-aid?' + query)
    assert response.status_code == 302
    assert response.location == destination
    assert client.get(response.location).status_code == 200


def test_retired_checklist_preserves_private_progress(app, parent):
    with app.app_context():
        item_id = db.session.scalar(db.select(ChecklistItem.id).where(ChecklistItem.slug == STEP_PREFIX + 'start'))
    response = post(parent, f'/checklist/{item_id}', {'completed': 'y', 'advance': '1'},
                    source='/checklist')
    assert response.location.endswith('/financial-aid?view=step&step=forms')
    page = parent.get('/financial-aid?view=review', follow_redirects=True).text
    assert 'Useful Tools' in page and 'prepared' not in page
    assert '0 of 5' in parent.get('/planning').text
    assert '/checklist/' + str(item_id) not in parent.get('/checklist').text
    with app.app_context():
        mark = db.session.scalar(db.select(UserChecklistProgress).where(UserChecklistProgress.item_id == item_id))
        assert mark.completed
