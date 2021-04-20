from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms import validators

class CreateVault(FlaskForm):
    vaultName = StringField('Vault name', validators=[validators.Length(min=1, max=17)])
    create = SubmitField('Create')