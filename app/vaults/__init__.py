from flask import Blueprint

vaults = Blueprint('vaults', __name__)

from . import views