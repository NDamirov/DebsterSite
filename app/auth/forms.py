from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import validators
# from ..validators import mainValidators

class LoginForm(FlaskForm):
    emailLog = StringField('Email', validators=[validators.Email('Invalid email')])
    password = PasswordField('Password', validators=[])
    log = SubmitField('Log in')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[validators.Email('Invalid email')])
    newUsername = StringField('Username', validators=[validators.Required()])
    password = PasswordField('Password', validators=[validators.Required()])
    passwordCopy = PasswordField('Password copy', validators=[ \
                   validators.EqualTo('password', message='Passwords must match')])
    recaptcha = RecaptchaField()
    register = SubmitField('Register')

class ConfirmForm(FlaskForm):
    token = StringField('Token')
    confirm = SubmitField('Confirm')

class RecoveryForm(FlaskForm):
    email = StringField('Email', validators=[validators.Email('Invalid email')])
    userName = StringField('Username')
    send = SubmitField('Send')

class PasswordEditForm(FlaskForm):
    password = PasswordField('Password', validators=[validators.Required()])
    passwordCopy = PasswordField('Password copy', validators = [\
                   validators.EqualTo('password', message='Password must match')])
    change = SubmitField('Change')
