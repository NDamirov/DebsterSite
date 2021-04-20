from . import api

from ..models import *
from .. import db

import requests


#Getting token
@api.route('/login')
def login():
    pass