"""Explicit, non-destructive local initialization and content seeding."""

import json
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import click
from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .aid_guidance import GUIDANCE, STEP_PREFIX
from .extensions import db
from .models import (
    ChecklistItem, OfficialDeadline, ParentInvitation, ParentQuestion, Reminder, Resource,
    SyntheticApplicant, SyntheticMilestone, SyntheticStudent, User, UserChecklistProgress,
)


def demo_email(email):
    try:
        return validate_email(email, check_deliverability=False).normalized.lower()
    except EmailNotValidError as error:
        raise click.ClickException(str(error)) from error


def write_public_content(session):
    content = json.loads(Path(__file__).with_name('content.json').read_text(encoding='utf-8'))
    resources = {}
    for values in content['resources']:
        values = dict(values)
        row = session.scalar(db.select(Resource).where(Resource.slug == values['slug']))
        if row is None:
            row = Resource(slug=values['slug'])
            session.add(row)
        for key, value in values.items():
            setattr(row, key, value)
        row.last_verified = date.fromisoformat(content['last_verified'])
        resources[row.slug] = row
    session.flush()
    aid_items = [
        dict(slug=STEP_PREFIX + key, title=title, responsibility=role, resource='aid')
        for key, title, role, *_ in GUIDANCE['steps']
    ]
    for position, values in enumerate([*content['checklist'], *aid_items]):
        row = session.scalar(db.select(ChecklistItem).where(ChecklistItem.slug == values['slug']))
        if row is None:
            row = ChecklistItem(slug=values['slug'])
            session.add(row)
        row.title = values['title']
        row.responsibility = values['responsibility']
        row.position = position
        row.resource = resources[values['resource']]
    for values in content['deadlines']:
        row = session.scalar(db.select(OfficialDeadline).where(OfficialDeadline.slug == values['slug']))
        if row is None:
            row = OfficialDeadline(slug=values['slug'])
            session.add(row)
        for key in ('round_name', 'admissions', 'financial_aid'):
            setattr(row, key, values[key])
        row.resource = resources[values['resource']]


def seed_content():
    """Refresh reviewed definitions, creating missing tables when needed."""
    prepare_database()


def prepare_database():
    """Create missing tables and seed public content in one startup transaction."""
    engine = db.engine
    with engine.begin() as connection:
        if connection.dialect.name == 'sqlite':
            # Take the write lock before checking which tables and seed rows exist.
            connection.exec_driver_sql('BEGIN IMMEDIATE')
        db.metadata.create_all(connection)
        with Session(bind=connection) as session:
            write_public_content(session)
            session.flush()


def register_commands(app):
    @app.cli.command('init-db')
    def init_db():
        """Create missing tables; never drop existing tables or user records."""
        db.create_all()
        click.echo('Database tables initialized.')

    @app.cli.command('prepare-db')
    def prepare_command():
        """Create missing tables and refresh public content without resetting data."""
        prepare_database()
        click.echo('Database prepared. Private data preserved.')

    @app.cli.command('seed-content')
    def content_command():
        """Insert or update reviewed public content, preserving private data."""
        seed_content()
        click.echo('Public content seeded. Private data preserved.')

    @app.cli.command('seed-invitations')
    @click.option('--email', required=True, help='Email of the local parent account that may accept the code.')
    @click.option('--count', type=click.IntRange(1, 20), default=1, show_default=True)
    def seed_invitations(email, count):
        """Create fictional applicants and pending invitations in local development."""
        if not app.debug or db.engine.dialect.name != 'sqlite':
            raise click.ClickException('Use a local SQLite development database with Flask --debug.')

        email = demo_email(email)

        expires_on = datetime.now(timezone.utc).date() + timedelta(days=7)
        generated = []
        for _ in range(count):
            number = f'SYN-{secrets.token_hex(8).upper()}'
            code = secrets.token_urlsafe(32)
            applicant = SyntheticApplicant(application_number=number, milestones=[
                SyntheticMilestone(position=1, title='Application started', completed=True),
                SyntheticMilestone(position=2, title='Application submitted', completed=False),
                SyntheticMilestone(position=3, title='Application review', completed=False),
                SyntheticMilestone(position=4, title='Decision available', completed=False),
            ])
            db.session.add(applicant)
            db.session.flush()
            db.session.add(ParentInvitation(
                applicant_id=applicant.id, invited_email=email, expires_on=expires_on,
                code_digest=ParentInvitation.digest_code(code),
            ))
            generated.append((number, code))
        db.session.commit()
        click.echo(f'Invited email: {email} (expires {expires_on} UTC)')
        for number, code in generated:
            click.echo(f'{number} invitation code: {code}')

    @app.cli.command('seed-student')
    @click.option('--email', required=True, help='Email for a new synthetic student account.')
    @click.option('--application-number', required=True, help='Existing fictional application number.')
    def seed_student(email, application_number):
        """Provision a separate student login in local development."""
        if not app.debug or db.engine.dialect.name != 'sqlite':
            raise click.ClickException('Use a local SQLite development database with Flask --debug.')
        email = demo_email(email)
        applicant = db.session.scalar(db.select(SyntheticApplicant).where(
            SyntheticApplicant.application_number == application_number,
        ))
        if applicant is None:
            raise click.ClickException('Fictional applicant not found.')
        password = secrets.token_urlsafe(18)
        user = User(email=email, student=SyntheticStudent(applicant_id=applicant.id))
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise click.ClickException('The email or applicant is already linked to an account.') from error
        click.echo(f'Local student email: {email}\nGenerated password (shown once): {password}')

    @app.cli.command('seed-demo')
    @click.option('--email', default='demo@example.com', show_default=True)
    def seed_demo(email):
        """Create a local demo account with a generated password, printed once."""
        email = demo_email(email)
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
