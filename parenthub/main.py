from datetime import date
from pathlib import Path

from flask import Blueprint, abort, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from .extensions import db
from .forms import AgeForm
from .models import ChecklistItem, OfficialDeadline, ParentQuestion, Reminder, Resource, UserChecklistProgress

bp = Blueprint('main', __name__)
ROOT = Path(__file__).resolve().parent.parent


@bp.get('/shared-css/<filename>')
def shared_css(filename):
    if filename not in {'styles.css', 'parent-guide.css'}:
        abort(404)
    return send_from_directory(ROOT / 'css', filename)


@bp.get('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html', title='Plan your Minerva journey')


@bp.get('/guide')
def guide():
    return render_template('guide.html', title='Parent guidance')


@bp.get('/financial-aid')
def financial_aid():
    return render_template('aid.html', title='Financial aid')


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = AgeForm(age_group=current_user.age_group)
    if form.validate_on_submit():
        current_user.age_group = form.age_group.data
        db.session.commit()
        flash('Age group saved.')
        return redirect(url_for('main.dashboard'))
    reminders = db.session.scalars(db.select(Reminder).where(
        Reminder.user_id == current_user.id, Reminder.completed.is_(False)
    ).order_by(Reminder.due_date, Reminder.id).limit(5)).all()
    total = db.session.scalar(db.select(db.func.count()).select_from(ChecklistItem))
    completed = db.session.scalar(db.select(db.func.count()).select_from(UserChecklistProgress).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.completed.is_(True)
    ))
    completed_ids = db.select(UserChecklistProgress.item_id).where(
        UserChecklistProgress.user_id == current_user.id, UserChecklistProgress.completed.is_(True)
    )
    next_item = db.session.scalar(db.select(ChecklistItem).where(
        ChecklistItem.responsibility == 'parent', ChecklistItem.id.not_in(completed_ids)
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
    return render_template('deadlines.html', title='Official deadlines', deadlines=rows)
