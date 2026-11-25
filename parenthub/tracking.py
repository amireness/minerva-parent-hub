"""Private planning routes; all record lookups are scoped to the owner."""

from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from .aid_guidance import STEP_PREFIX
from .extensions import db
from .forms import ProgressForm, QuestionForm, ReminderForm
from .models import ChecklistItem, ParentQuestion, Reminder, UserChecklistProgress

bp = Blueprint('tracking', __name__)


def owned_record(model, record_id):
    """Return an owned record or the same 404 used for a missing record."""
    return db.first_or_404(db.select(model).where(model.id == record_id, model.user_id == current_user.id))


@bp.get('/checklist')
@login_required
def checklist():
    items = db.session.scalars(db.select(ChecklistItem).where(~ChecklistItem.slug.startswith(STEP_PREFIX))
                               .order_by(ChecklistItem.position)).all()
    completed = set(db.session.scalars(db.select(UserChecklistProgress.item_id).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.completed.is_(True)
    )).all())
    return render_template('checklist.html', title='Admissions checklist', items=items,
                           completed=completed, form=ProgressForm())


@bp.post('/checklist/<int:item_id>')
@login_required
def update_progress(item_id):
    item = db.get_or_404(ChecklistItem, item_id)
    aid_step = item.slug.startswith(STEP_PREFIX)
    if aid_step and current_user.student:
        abort(404)
    form = ProgressForm()
    if not form.validate_on_submit():
        abort(400)
    progress = db.session.scalar(db.select(UserChecklistProgress).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.item_id == item_id
    ))
    if progress is None:
        progress = UserChecklistProgress(user_id=current_user.id, item_id=item_id)
        db.session.add(progress)
    progress.completed = form.completed.data
    db.session.commit()
    flash('Checklist updated.')
    if aid_step:
        return redirect(url_for('main.financial_aid', _anchor='step-' + item.slug.removeprefix(STEP_PREFIX)))
    return redirect(url_for('tracking.checklist'))


@bp.get('/reminders')
@login_required
def reminders():
    rows = db.session.scalars(db.select(Reminder).where(Reminder.user_id == current_user.id)
                             .order_by(Reminder.completed, Reminder.due_date, Reminder.id)).all()
    return render_template('reminders.html', title='Personal reminders', reminders=rows,
                           today=date.today(), delete_form=FlaskForm())


@bp.route('/reminders/new', methods=['GET', 'POST'])
@bp.route('/reminders/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reminder(record_id=None):
    reminder = owned_record(Reminder, record_id) if record_id is not None else None
    form = ReminderForm(obj=reminder)
    if form.validate_on_submit():
        if reminder is None:
            reminder = Reminder(user_id=current_user.id)
            db.session.add(reminder)
        form.populate_obj(reminder)
        db.session.commit()
        flash('Reminder saved.')
        return redirect(url_for('tracking.reminders'))
    return render_template('form.html', title='Edit reminder' if reminder else 'Create reminder',
                           form=form, private=True, back=url_for('tracking.reminders')), 422 if form.is_submitted() else 200


@bp.post('/reminders/<int:record_id>/delete')
@login_required
def delete_reminder(record_id):
    reminder = owned_record(Reminder, record_id)
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted.')
    return redirect(url_for('tracking.reminders'))


@bp.get('/questions')
@login_required
def questions():
    rows = db.session.scalars(db.select(ParentQuestion).where(ParentQuestion.user_id == current_user.id)
                             .order_by(ParentQuestion.resolved, ParentQuestion.id.desc())).all()
    return render_template('questions.html', title='Questions for Admissions', questions=rows, delete_form=FlaskForm())


@bp.route('/questions/new', methods=['GET', 'POST'])
@bp.route('/questions/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(record_id=None):
    question = owned_record(ParentQuestion, record_id) if record_id is not None else None
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        if question is None:
            question = ParentQuestion(user_id=current_user.id)
            db.session.add(question)
        form.populate_obj(question)
        db.session.commit()
        flash('Question saved.')
        return redirect(url_for('tracking.questions'))
    return render_template('form.html', title='Edit question' if question else 'Save a question',
                           form=form, private=True, back=url_for('tracking.questions')), 422 if form.is_submitted() else 200


@bp.post('/questions/<int:record_id>/delete')
@login_required
def delete_question(record_id):
    question = owned_record(ParentQuestion, record_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted.')
    return redirect(url_for('tracking.questions'))
