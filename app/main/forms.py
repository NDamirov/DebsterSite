from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from ..validators import mainValidators

class DebtConfirmation(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')

class CreateDebt(FlaskForm):
    debtTo = StringField('Debt to')
    total = IntegerField('Total', validators=[mainValidators.IntegerRequired])
    description = TextAreaField('Description')
    create = SubmitField('Create')