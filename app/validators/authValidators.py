from wtforms import ValidationError, validators
from ..models import User

def userLoginEmail(form, field):
    data = str(field.data)
    if len(data) > 64:
        raise ValidationError("Your email is too long")

    validators.Email(message='Invalid email').__call__(form, field)

def userPassword(form, field, email):
    raise ValidationError("Wrong password")
