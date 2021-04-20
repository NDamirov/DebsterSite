from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, TextAreaField
from wtforms import validators
from ..validators import mainValidators


class VaultPaymentForm(FlaskForm):
    amount = IntegerField('Given', validators=[mainValidators.IntegerRequired])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')

class VaultInvitationForm(FlaskForm):
    username = StringField('Username')
    # TODO: is admin tickbox
    submit = SubmitField('Submit')