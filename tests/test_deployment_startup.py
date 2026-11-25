from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import inspect

from parenthub import create_app
from parenthub import commands
from parenthub.extensions import db
from parenthub.models import ChecklistItem, OfficialDeadline, Resource, User, UserChecklistProgress


@pytest.fixture
def render_database(monkeypatch, tmp_path):
    monkeypatch.setenv('RENDER', 'true')
    monkeypatch.setenv('SECRET_KEY', 'startup-test-secret')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///' + (tmp_path / 'render.sqlite').as_posix())


def test_render_startup_serves_seeded_pages_without_cli(render_database):
    app = create_app()
    with app.test_client() as client:
        deadlines = client.get('/deadlines')
        assert deadlines.status_code == 200
        assert 'January 5' in deadlines.text
        assert 'Official application process and deadlines' in client.get('/resources').text
        assert 'What is financial aid?' in client.get('/financial-aid').text
        assert 'Useful Tools' in client.get('/financial-aid?view=review', follow_redirects=True).text
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(ChecklistItem)) == 12
        assert inspect(db.engine).has_table('aid_document')
        db.engine.dispose()


def test_concurrent_render_starts_keep_seed_ids_and_private_progress(render_database):
    def start():
        app = create_app()
        with app.app_context():
            ids = db.session.execute(db.select(OfficialDeadline.slug, OfficialDeadline.id)).all()
            db.session.remove()
            db.engine.dispose()
            return ids

    with ThreadPoolExecutor(max_workers=3) as workers:
        results = list(workers.map(lambda _: start(), range(3)))
    assert len(results[0]) == 3 and results[0] == results[1] == results[2]

    app = create_app()
    with app.app_context():
        user = User(email='parent@example.com')
        user.set_password('test-password')
        item = db.session.scalar(db.select(ChecklistItem).where(ChecklistItem.slug == 'first-aid-start'))
        db.session.add(UserChecklistProgress(user=user, item=item, completed=True))
        db.session.commit()
        ids = user.id, item.id
        db.session.remove()
        db.engine.dispose()

    second = create_app()
    assert second.test_cli_runner().invoke(args=['prepare-db']).exit_code == 0
    with second.app_context():
        mark = db.session.scalar(db.select(UserChecklistProgress))
        assert (mark.user_id, mark.item_id, mark.completed) == (*ids, True)
        assert db.session.scalar(db.select(db.func.count()).select_from(Resource)) == 6
        db.session.remove()
        db.engine.dispose()


def test_failed_render_seed_rolls_back_and_next_start_retries(render_database, monkeypatch):
    write_content = commands.write_public_content

    def fail(session):
        write_content(session)
        raise RuntimeError('simulated seed failure')

    with monkeypatch.context() as patch:
        patch.setattr(commands, 'write_public_content', fail)
        with pytest.raises(RuntimeError, match='simulated seed failure'):
            create_app()

    app = create_app({'PREPARE_DATABASE_ON_STARTUP': False})
    with app.app_context():
        assert not inspect(db.engine).has_table('official_deadline')
        db.engine.dispose()
    assert create_app().test_client().get('/deadlines').status_code == 200
