"""Relational records for public content and private parent planning."""

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age_group = db.Column(db.String(10), nullable=True)
    __table_args__ = (CheckConstraint("age_group IN ('under18', 'adult')"),)

    progress = db.relationship('UserChecklistProgress', back_populates='user', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', back_populates='user', cascade='all, delete-orphan')
    questions = db.relationship('ParentQuestion', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(160), nullable=False)
    topic = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    last_verified = db.Column(db.Date, nullable=False)
    checklist_items = db.relationship('ChecklistItem', back_populates='resource')
    deadlines = db.relationship('OfficialDeadline', back_populates='resource')


class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    responsibility = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    resource = db.relationship('Resource', back_populates='checklist_items')
    progress = db.relationship('UserChecklistProgress', back_populates='item', cascade='all, delete-orphan')
    __table_args__ = (CheckConstraint("responsibility IN ('parent', 'applicant')"),)


class UserChecklistProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('checklist_item.id'), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', back_populates='progress')
    item = db.relationship('ChecklistItem', back_populates='progress')
    __table_args__ = (UniqueConstraint('user_id', 'item_id'),)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', back_populates='reminders')


class ParentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    body = db.Column(db.String(1000), nullable=False)
    resolved = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', back_populates='questions')


class OfficialDeadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    round_name = db.Column(db.String(80), nullable=False)
    admissions = db.Column(db.String(30), nullable=False)
    financial_aid = db.Column(db.String(30), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    resource = db.relationship('Resource', back_populates='deadlines')
