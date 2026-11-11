from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length


def stripped(value):
    return value.strip() if value else value


class LoginForm(FlaskForm):
    email = StringField('Email', filters=[stripped], validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])


class RegisterForm(LoginForm):
    password = PasswordField('Password (12–128 characters)', validators=[InputRequired(), Length(min=12, max=128)])
    confirm = PasswordField('Confirm password', validators=[InputRequired(), EqualTo('password')])


class AgeForm(FlaskForm):
    age_group = SelectField("Your child's age group", choices=[('under18', 'Under 18'), ('adult', '18 or older')], validators=[DataRequired()])


class ProgressForm(FlaskForm):
    completed = BooleanField('Completed')


class ReminderForm(FlaskForm):
    title = StringField('Reminder', filters=[stripped], validators=[DataRequired(), Length(max=160)])
    due_date = DateField('Date', validators=[InputRequired()])
    completed = BooleanField('Completed')


class QuestionForm(FlaskForm):
    body = TextAreaField('Question for Admissions', filters=[stripped], validators=[DataRequired(), Length(max=1000)])
    resolved = BooleanField('Resolved')
