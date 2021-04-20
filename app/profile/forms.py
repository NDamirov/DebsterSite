from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms import validators

class UsernameChange(FlaskForm):
    newUsername = StringField('New username', validators=[validators.Required()])
    change = SubmitField('Change')

class PasswordChange(FlaskForm):
    newPassword = PasswordField('New password', validators=[validators.Required()])
    newPasswordCopy = PasswordField('New password', validators=[ \
                        validators.EqualTo('newPassword', message='Passwords must match')])
    change = SubmitField('Change')