from wtforms import ValidationError
import re

def isInteger(line):
    lineToInt = 0
    for i in line:
        lineToInt *= 10


def IntegerRequired(form, field):
    data = str(field.data)

    if len(data) == 0:
        raise ValidationError('Empty field')

    if len(data) > 9:
        raise ValidationError('Too long field')

    return True

#HTML purifier
def pure(text):
    text.replace('<', '&lt;')
    text.replace('>', '&gt;')
    return text

def badUsername(username):
    return re.search(r'[^a-zA-z0-9,\._!&\*\+-]', username) is None
