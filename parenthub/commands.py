"""Explicit, non-destructive local initialization and content seeding."""

import json
import secrets
from datetime import date, timedelta
from pathlib import Path

import click

from .extensions import db
from .models import ChecklistItem, OfficialDeadline, ParentQuestion, Reminder, Resource, User, UserChecklistProgress


def seed_content():
    """Upsert reviewed definitions without changing IDs or private records."""
    content = json.loads(Path(__file__).with_name('content.json').read_text(encoding='utf-8'))
    resources = {}
    for values in content['resources']:
        values = dict(values)
        row = db.session.scalar(db.select(Resource).where(Resource.slug == values['slug']))
        if row is None:
            row = Resource(slug=values['slug'])
            db.session.add(row)
        for key, value in values.items():
            setattr(row, key, value)
        row.last_verified = date.fromisoformat(content['last_verified'])
        resources[row.slug] = row
    db.session.flush()
    for position, values in enumerate(content['checklist']):
        row = db.session.scalar(db.select(ChecklistItem).where(ChecklistItem.slug == values['slug']))
        if row is None:
            row = ChecklistItem(slug=values['slug'])
            db.session.add(row)
        row.title = values['title']
        row.responsibility = values['responsibility']
        row.position = position
        row.resource = resources[values['resource']]
    for values in content['deadlines']:
        row = db.session.scalar(db.select(OfficialDeadline).where(OfficialDeadline.slug == values['slug']))
        if row is None:
            row = OfficialDeadline(slug=values['slug'])
            db.session.add(row)
        for key in ('round_name', 'admissions', 'financial_aid'):
            setattr(row, key, values[key])
        row.resource = resources[values['resource']]
    db.session.commit()


def register_commands(app):
    @app.cli.command('init-db')
    def init_db():
        """Create missing tables; never drop existing tables or user records."""
        db.create_all()
        click.echo('Database tables initialized.')

    @app.cli.command('seed-content')
    def content_command():
        """Insert or update reviewed public content, preserving private data."""
        seed_content()
        click.echo('Public content seeded. Private data preserved.')

    @app.cli.command('seed-demo')
    @click.option('--email', default='demo@example.com', show_default=True)
    def seed_demo(email):
        """Create a local demo account with a generated password, printed once."""
        from email_validator import EmailNotValidError, validate_email
        try:
            email = validate_email(email, check_deliverability=False).normalized.lower()
        except EmailNotValidError as error:
            raise click.ClickException(str(error)) from error
        if db.session.scalar(db.select(User).where(User.email == email)):
            raise click.ClickException('Account already exists; its password and data were not changed.')
        seed_content()
        password = secrets.token_urlsafe(18)
        user = User(email=email, age_group='under18')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        item = db.session.scalar(db.select(ChecklistItem).where(ChecklistItem.slug == 'parent-resources'))
        db.session.add(UserChecklistProgress(user=user, item=item, completed=True))
        db.session.add(Reminder(user=user, title='Contact Admissions', due_date=date.today() + timedelta(days=7)))
        db.session.add(ParentQuestion(user=user, body='Which steps, if any, require a parent?'))
        db.session.commit()
        click.echo(f'Local demo email: {email}\nGenerated password (shown once): {password}')
