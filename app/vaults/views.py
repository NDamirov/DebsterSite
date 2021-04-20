from . import vaults
from .forms import CreateVault

from ..models import User, Vault, VaultPayment, VaultSubscription
from ..basicFunctions.vaultFunctions import *

from flask import render_template, redirect, url_for, request, flash, make_response
from flask_login import current_user


# Only authorized users can acess this blueprint
@vaults.before_request
def restrictMain():
    if not current_user.is_authenticated or \
       not current_user._get_current_object().confirmedAccount:
        flash('You must log in')
        return redirect(url_for('auth.main'))

    if not 'pver' in request.cookies or \
       request.cookies.get('pver') != current_user._get_current_object().password_ver:
        flash('You must log in')
        logout_user()
        return redirect(url_for('auth.main'))

@vaults.route('/')
def main():
    user = current_user._get_current_object()
    vaults = user.vaults.filter((VaultSubscription.state==1)|(VaultSubscription.state==2)).all()
    # print(vaults[0].vault.name)
    return render_template('/vaults/main.html', vaults=vaults)

@vaults.route('/invitations')
def invitations():
    user = current_user._get_current_object()
    vaults = user.vaults.filter_by(state=0).all()
    return render_template('/vaults/invitations.html', vaults=vaults)

@vaults.route('/create', methods=['POST', 'GET'])
def create():
    form = CreateVault(request.form)
    if request.method == 'POST' and form.validate():
        user = current_user._get_current_object()
        name = str(form.vaultName.data)

        createVault(user, name)

        return redirect(url_for('vaults.main'))
    return render_template('/vaults/create.html', form=form)

@vaults.route('/confirm/<id>', methods=['GET'])
def confirm(id):
    try:
        id = int(id)
    except:
        return redirect(url_for('vaults.invitations'))

    subscription = VaultSubscription.query.get(id)
    user = current_user._get_current_object()

    if subscription is not None:
        confirmInvitation(user, subscription)
    
    return redirect(url_for('vaults.invitations'))

@vaults.route('/reject/<id>', methods=['GET'])
def reject(id):
    try:
        id = int(id)
    except:
        return redirect(url_for('vaults.invitations'))

    subscription = VaultSubscription.query.get(id)
    user = current_user._get_current_object()

    if subscription is not None:
        rejectInvitation(user, subscription)
    
    return redirect(url_for('vaults.invitations'))

