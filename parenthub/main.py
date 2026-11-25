import json
from datetime import date, datetime, timezone
from pathlib import Path

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.dialects.sqlite import insert

from .aid_guidance import GUIDANCE, STEP_PREFIX
from .deadline_events import ADMISSIONS_URL, calendar_bytes, homepage_deadline, upcoming_events
from .extensions import db
from .forms import AgeForm, AidDocumentForm, InvitationForm, ProgressForm
from .models import (
    AidDocument, ChecklistItem, OfficialDeadline, ParentInvitation, ParentQuestion, Reminder,
    Resource, SyntheticApplicant, SyntheticApplicantRound, User, UserChecklistProgress,
)

bp = Blueprint('main', __name__)
ROOT = Path(__file__).resolve().parent.parent
AID_EXAMPLES = json.loads(Path(__file__).with_name('aid_examples.json').read_text(encoding='utf-8'))
AID_CATEGORIES = {item['key']: item for item in AID_EXAMPLES['documents']}
STAGE_EXPLANATIONS = {
    'Application started': 'Your applicant has begun working on the application.',
    'Application submitted': 'Your applicant has finished and sent in the application.',
    'Application review': 'The submitted application is being considered in this example.',
    'Decision available': 'Your applicant can check the decision and decide what to do next.',
    'Enrollment preparation': 'Your applicant can review enrollment steps if they choose to attend.',
}


def utc_today():
    return datetime.now(timezone.utc).date()


def linked_applicants():
    return db.session.scalars(db.select(SyntheticApplicant).join(ParentInvitation).where(
        *ParentInvitation.valid_for(current_user, utc_today()),
        ParentInvitation.accepted_by_id == current_user.id,
    ).order_by(SyntheticApplicant.id)).unique().all()


def application_journeys(applicants):
    journeys = []
    for applicant in applicants:
        milestones = applicant.milestones
        next_index = next((index for index, milestone in enumerate(milestones)
                           if not milestone.completed), len(milestones))
        current = milestones[next_index - 1] if next_index else None
        upcoming = milestones[next_index] if next_index < len(milestones) else None
        explanation = (STAGE_EXPLANATIONS.get(current.title, 'This is the latest stage reached in the example.')
                       if current else 'Your applicant has yet to reach the first stage.' if milestones
                       else 'There are no example stages for this application yet.')
        journeys.append((applicant, current, upcoming, explanation))
    return journeys


def sample_filename(category, sample):
    stem = AID_CATEGORIES[category]['filename']
    return f'{stem}-example-{sample}.pdf'


@bp.get('/shared-css/<filename>')
def shared_css(filename):
    if filename not in {'styles.css', 'parent-guide.css'}:
        abort(404)
    return send_from_directory(ROOT / 'css', filename)


@bp.get('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    now = datetime.now(timezone.utc)
    return render_template('home.html', title='Support your Minerva applicant',
                           deadline=homepage_deadline(now), now=now, admissions_url=ADMISSIONS_URL)


@bp.get('/guide')
def guide():
    return render_template('guide.html', title='Parent guidance')


@bp.get('/help')
def help_center():
    return render_template('help.html', title='Help')


@bp.get('/financial-aid')
def financial_aid():
    applicants = linked_applicants() if current_user.is_authenticated and not current_user.student else []
    applicant_id = request.args.get('applicant', type=int)
    applicant = next((item for item in applicants if item.id == applicant_id), None)
    if applicant_id is not None and applicant is None:
        abort(404)
    if applicant is None and applicants:
        applicant = applicants[0]
    return render_financial_aid(applicants, applicant)


def render_financial_aid(applicants, applicant, failed_category=None, form=None):
    focused_category = failed_category or request.args.get('category')
    view = request.args.get('view')
    if failed_category or (view is None and (focused_category or 'applicant' in request.args)):
        view = 'documents'
    view = view or 'overview'
    if view not in {'overview', 'learn', 'step', 'review', 'documents', 'process', 'glossary', 'translations', 'currency'}:
        abort(404)
    topics = GUIDANCE['topics']
    topic_keys = [topic['key'] for topic in topics]
    topic_key = request.args.get('topic', topic_keys[0])
    if view == 'learn' and topic_key not in topic_keys:
        abort(404)
    topic_index = topic_keys.index(topic_key) if view == 'learn' else None
    saved = {}
    step_records = {}
    if current_user.is_authenticated and not current_user.student:
        step_records = {
            slug: (item_id, bool(done))
            for slug, item_id, done in db.session.execute(
                db.select(ChecklistItem.slug, ChecklistItem.id, UserChecklistProgress.completed)
                .outerjoin(UserChecklistProgress, (UserChecklistProgress.item_id == ChecklistItem.id)
                           & (UserChecklistProgress.user_id == current_user.id))
                .where(ChecklistItem.slug.startswith(STEP_PREFIX))
            )
        }
    steps = GUIDANCE['steps']
    step_keys = [step[0] for step in steps]
    next_step = next((step for step in steps
                      if not step_records.get(STEP_PREFIX + step[0], (None, False))[1]), None)
    step_key = request.args.get('step') or (next_step or steps[-1])[0]
    if view == 'step' and step_key not in step_keys:
        abort(404)
    step_index = step_keys.index(step_key) if view == 'step' else None
    return_step = request.args.get('return_step')

    def aid_link(destination, **params):
        return url_for('main.financial_aid', view=destination, applicant=applicant.id if applicant else None, **params)

    if applicant and view == 'documents':
        saved = {row.category: row for row in db.session.scalars(db.select(AidDocument).where(
            AidDocument.parent_id == current_user.id, AidDocument.applicant_id == applicant.id,
            AidDocument.category.in_(AID_CATEGORIES),
        ))}
        if form is None and focused_category in AID_CATEGORIES:
            form = AidDocumentForm()
            form.sample.choices = [(sample, sample_filename(focused_category, sample)) for sample in (1, 2)]
    return render_template('aid.html', title='Financial Aid', examples=AID_EXAMPLES,
                           applicants=applicants, applicant=applicant, form=form, saved=saved,
                           focused_category=focused_category, sample_filename=sample_filename,
                           guidance=GUIDANCE, step_records=step_records, step_prefix=STEP_PREFIX,
                           next_step=next_step, progress_form=ProgressForm(), view=view,
                           step_index=step_index, aid_link=aid_link, topic_index=topic_index,
                           completed_count=sum(done for _, done in step_records.values()),
                           return_step=return_step if return_step in step_keys else None)


@bp.get('/aid-preparation')
@login_required
def aid_preparation():
    return redirect(url_for('main.financial_aid'))


def parent_document_scope(applicant_id, category):
    applicants = linked_applicants() if not current_user.student else []
    applicant = next((item for item in applicants if item.id == applicant_id), None)
    if applicant is None or category not in AID_CATEGORIES:
        abort(404)
    scope = (AidDocument.parent_id == current_user.id, AidDocument.applicant_id == applicant.id,
             AidDocument.category == category)
    return applicants, applicant, scope


@bp.post('/financial-aid/<int:applicant_id>/<category>/<action>')
@login_required
def manage_document(applicant_id, category, action):
    applicants, applicant, scope = parent_document_scope(applicant_id, category)
    if action == 'link':
        form = AidDocumentForm()
        form.sample.choices = [(sample, sample_filename(category, sample)) for sample in (1, 2)]
        if not form.validate_on_submit():
            return render_financial_aid(applicants, applicant, category, form), 422
        statement = insert(AidDocument).values(
            parent_id=current_user.id, applicant_id=applicant.id, category=category,
            sample=form.sample.data, shared=False,
        )
        db.session.execute(statement.on_conflict_do_update(
            index_elements=['parent_id', 'applicant_id', 'category'],
            set_={'sample': form.sample.data, 'shared': False},
        ))
        message = 'Example document linked.'
    elif action in ('remove', 'share', 'unshare'):
        if action == 'remove':
            statement = db.delete(AidDocument).where(*scope)
            message = 'Document link removed.'
        else:
            statement = db.update(AidDocument).where(*scope).values(shared=action == 'share')
            message = 'Document presence shared.' if action == 'share' else 'Document is private again.'
        if db.session.execute(statement).rowcount != 1:
            abort(404)
    else:
        abort(404)
    db.session.commit()
    flash(message)
    return redirect(url_for('main.financial_aid', view='documents', applicant=applicant.id,
                            return_step=request.args.get('return_step'), _anchor=category))


@bp.get('/financial-aid/<int:applicant_id>/<category>/open')
@login_required
def open_document(applicant_id, category):
    _, _, scope = parent_document_scope(applicant_id, category)
    sample = db.session.scalar(db.select(AidDocument.sample).where(*scope))
    if sample is None:
        abort(404)
    return render_template('aid_document.html', title=sample_filename(category, sample),
                           applicant_id=applicant_id, category=category)


@bp.get('/student/preparation')
@login_required
def student_preparation():
    student = current_user.student
    if student is None:
        abort(404)
    invitation_exists = db.select(ParentInvitation.id).join(User, User.id == ParentInvitation.accepted_by_id).where(
        ParentInvitation.applicant_id == AidDocument.applicant_id,
        ParentInvitation.accepted_by_id == AidDocument.parent_id,
        ParentInvitation.invited_email == User.email,
        ParentInvitation.expires_on > utc_today(),
        ParentInvitation.revoked_on.is_(None),
    ).exists()
    shared = db.session.scalars(db.select(AidDocument.category).where(
        AidDocument.applicant_id == student.applicant_id, AidDocument.shared.is_(True),
        AidDocument.category.in_(AID_CATEGORIES), invitation_exists,
    ).distinct().order_by(AidDocument.category)).all()
    return render_template('student_preparation.html', title='Shared documents',
                           shared=shared, categories=AID_CATEGORIES)


@bp.get('/application-progress')
@login_required
def application_progress():
    applicants = linked_applicants() if not current_user.student else []
    if not applicants:
        return redirect(url_for('main.dashboard'))
    return render_template('application_progress.html', title='Application progress',
                           journeys=application_journeys(applicants), stage_explanations=STAGE_EXPLANATIONS)


@bp.get('/account')
@login_required
def account():
    if current_user.student:
        return redirect(url_for('main.student_preparation'))
    return render_template('account.html', title='Account', form=InvitationForm())


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.student:
        return redirect(url_for('main.student_preparation'))
    today = utc_today()
    valid = ParentInvitation.valid_for(current_user, today)
    form = InvitationForm()
    if form.validate_on_submit():
        claimed = db.session.execute(db.update(ParentInvitation).where(
            *valid,
            ParentInvitation.code_digest == ParentInvitation.digest_code(form.code.data),
            ParentInvitation.accepted_by_id.is_(None),
        ).values(accepted_by_id=current_user.id, accepted_on=today))
        if claimed.rowcount == 1:
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        db.session.rollback()
        form.code.errors.append('This invitation code is unavailable for your account.')

    applicants = linked_applicants()
    if applicants:
        if form.is_submitted():
            return render_template('account.html', title='Account', form=form), 422
        active = db.session.scalars(db.select(AidDocument).where(
            AidDocument.parent_id == current_user.id,
            AidDocument.applicant_id.in_([applicant.id for applicant in applicants]),
            AidDocument.category.in_(AID_CATEGORIES),
        ).order_by(AidDocument.applicant_id, AidDocument.category)).first()
        action = 'Review linked documents' if active else 'Review financial aid documents'
        action_url = url_for('main.financial_aid', view='documents' if active else None,
                             applicant=active.applicant_id if active else None)
        rounds = db.session.scalars(db.select(SyntheticApplicantRound.round_slug).where(
            SyntheticApplicantRound.applicant_id.in_([applicant.id for applicant in applicants]),
        )).all()
        now = datetime.now(timezone.utc)
        return render_template('applicant_dashboard.html', title='Welcome to Parent Hub',
                               journeys=application_journeys(applicants), action=action, action_url=action_url,
                               deadline=homepage_deadline(now, rounds), now=now, admissions_url=ADMISSIONS_URL)
    now = datetime.now(timezone.utc)
    return render_template('invitation_required.html', title='Invitation required',
                           form=form, deadline=homepage_deadline(now), now=now,
                           admissions_url=ADMISSIONS_URL), 422 if form.is_submitted() else 200


@bp.route('/planning', methods=['GET', 'POST'])
@login_required
def planning():
    form = AgeForm(age_group=current_user.age_group)
    if form.validate_on_submit():
        current_user.age_group = form.age_group.data
        db.session.commit()
        flash('Age group saved.')
        return redirect(url_for('main.planning'))
    reminders = db.session.scalars(db.select(Reminder).where(
        Reminder.user_id == current_user.id, Reminder.completed.is_(False)
    ).order_by(Reminder.due_date, Reminder.id).limit(5)).all()
    admissions_item = ~ChecklistItem.slug.startswith(STEP_PREFIX)
    total = db.session.scalar(db.select(db.func.count()).select_from(ChecklistItem).where(admissions_item))
    completed = db.session.scalar(db.select(db.func.count()).select_from(UserChecklistProgress)
                                  .join(ChecklistItem).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.completed.is_(True),
        admissions_item,
    ))
    completed_ids = db.select(UserChecklistProgress.item_id).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.completed.is_(True)
    )
    next_item = db.session.scalar(db.select(ChecklistItem).where(
        admissions_item, ChecklistItem.responsibility == 'parent', ChecklistItem.id.not_in(completed_ids)
    ).order_by(ChecklistItem.position).limit(1))
    questions = db.session.scalars(db.select(ParentQuestion).where(
        ParentQuestion.user_id == current_user.id, ParentQuestion.resolved.is_(False)
    ).order_by(ParentQuestion.id.desc()).limit(3)).all()
    featured = db.session.scalars(db.select(Resource).where(
        Resource.slug.in_(['admissions', 'families', 'aid'])
    ).order_by(Resource.id)).all()
    return render_template('dashboard.html', title='Your dashboard', form=form, reminders=reminders,
                           total=total, completed=completed, today=date.today(), next_item=next_item,
                           questions=questions, featured=featured), 422 if form.is_submitted() else 200


@bp.get('/resources')
def resources():
    query = request.args.get('q', '').strip()[:160]
    topic = request.args.get('topic', '').strip()[:40]
    statement = db.select(Resource)
    if query:
        statement = statement.where(or_(Resource.title.icontains(query, autoescape=True),
                                       Resource.description.icontains(query, autoescape=True)))
    if topic:
        statement = statement.where(Resource.topic == topic)
    topics = db.session.scalars(db.select(Resource.topic).distinct().order_by(Resource.topic)).all()
    return render_template('resources.html', title='Resource library',
                           resources=db.session.scalars(statement.order_by(Resource.title)).all(),
                           query=query, topic=topic, topics=topics)


@bp.get('/deadlines')
def deadlines():
    rows = db.session.scalars(db.select(OfficialDeadline).order_by(OfficialDeadline.id)).all()
    now = datetime.now(timezone.utc)
    return render_template('deadlines.html', title='Deadlines', deadlines=rows,
                           events=upcoming_events(now), now=now, admissions_url=ADMISSIONS_URL)


@bp.get('/deadlines/<slug>.ics')
def deadline_calendar(slug):
    now = datetime.now(timezone.utc)
    event = next((event for event in upcoming_events(now) if event.slug == slug), None)
    if event is None:
        abort(404)
    return Response(calendar_bytes(event, now), content_type='text/calendar; charset=utf-8',
                    headers={'Content-Disposition': f'attachment; filename="{event.slug}.ics"'})
