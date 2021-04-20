from . import vault
from .forms import VaultPaymentForm, VaultInvitationForm

from ..models import User, Vault, VaultPayment, VaultSubscription, PaymentState
from ..basicFunctions.vaultFunctions import *

from flask import render_template, redirect, url_for, request, flash, make_response
from flask_login import current_user

from wtforms import ValidationError

# Only authorized users can acess this blueprint
@vault.before_request
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

@vault.route('/<id>/<page>')
def showVault(id, page):
    try:
        id = int(id)
        page = int(page)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(id)

    if vault is None:
        return redirect(url_for('vaults.main'))

    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    payments = vault.payments.order_by(VaultPayment.id.desc()).limit(15).all()

    return render_template('/vault/main.html', id=id, isAdmin=(subscription.state == 2), \
            payments=payments, total=vault.total, notConfirmedTotal=vault.NotConfirmedTotal)

@vault.route('/history/<id>/<page>')
def history(id, page):
    try:
        id = int(id)
        page = int(page)
    except:
        return redirect(url_for('vaults.main'))

    if page < 0:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(id)

    if vault is None:
        return redirect(url_for('vaults.main'))

    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    payments = vault.payments.order_by(VaultPayment.id.desc()).offset(15 * page).limit(15).all()

    return render_template('/vault/history.html', id=id, isAdmin=(subscription.state == 2), \
            payments=payments, page=page, paymentsAmount=vault.paymentsAmount)


@vault.route('/give/<id>', methods=['POST', 'GET'])
def give(id):
    try:
        id = int(id)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(id)

    if vault is None:
        return redirect(url_for('vaults.main'))

    form = VaultPaymentForm(request.form)

    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    if request.method == 'POST' and form.submit.data and form.validate():
        amount = int(form.amount.data)

        # form validating
        if amount <= 0 or amount > 999999999 or len(form.description.data) > 150:
            form.amount.errors += (ValidationError('Invalid input'),)
            return render_template('/vault/give.html', id=id, form=form, isAdmin=(subscription.state == 2))

        createPayment(vault, user, amount, form.description.data)
        return redirect(url_for('vaults.main'))
        
    return render_template('/vault/give.html', id=id, form=form, isAdmin=(subscription.state == 2))


@vault.route('/take/<id>', methods=['POST', 'GET'])
def take(id):
    try:
        id = int(id)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(id)

    if vault is None:
        return redirect(url_for('vaults.main'))

    form = VaultPaymentForm(request.form)

    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    if request.method == 'POST' and form.submit.data and form.validate():
        amount = int(form.amount.data)

        # form validating
        if amount <= 0 or amount > 999999999 or len(form.description.data) > 150:
            form.amount.errors += (ValidationError('Invalid input'),)
            return render_template('/vault/give.html', id=id, form=form, isAdmin=(subscription.state == 2))

        createPayment(vault, user, -amount, form.description.data)
        return redirect(url_for('vaults.main'))
        
    return render_template('/vault/take.html', id=id, form=form, isAdmin=(subscription.state == 2))

@vault.route('/confirm/<vaultId>/<paymentId>')
def confirm(vaultId, paymentId):
    try:
        vaultId = int(vaultId)
        paymentId = int(paymentId)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(vaultId)
    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    payment = VaultPayment.query.get(paymentId)

    if payment is None:
        return redirect(url_for('vaults.main'))

    confirmPayment(vault, payment, user)

    return redirect(url_for('vault.showVault', id=vaultId, page=0))

@vault.route('/reject/<vaultId>/<paymentId>')
def reject(vaultId, paymentId):
    try:
        vaultId = int(vaultId)
        paymentId = int(paymentId)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(vaultId)
    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    payment = VaultPayment.query.get(paymentId)

    if payment is None:
        return redirect(url_for('vaults.main'))

    rejectPayment(vault, payment, user)

    return redirect(url_for('vault.showVault', id=vaultId, page=0))

    

@vault.route('/invite/<id>', methods=['POST', 'GET'])
def invite(id):
    try:
        id = int(id)
    except:
        return redirect(url_for('vaults.main'))

    vault = Vault.query.get(id)

    if vault is None:
        return redirect(url_for('vaults.main'))

    user = current_user._get_current_object()

    subscription = vault.users.filter_by(user_id=user.id).first()
    if subscription is None or subscription.state == 0 \
       or subscription.state == 3:
        return redirect(url_for('vaults.main'))

    form = VaultInvitationForm(request.form)

    if request.method == 'POST':
        userTo = User.query.filter_by(username=str(form.username.data)).first()
        if userTo is None:
            form.username.errors += (ValidationError('No such username'), )
            return render_template('/vault/invite.html', id=id, form=form, isAdmin=(subscription.state == 2))

        if vault.users.filter_by(user_id=userTo.id).first() is not None:
            form.username.errors += (ValidationError('This user can\'t be invited'), )
            return render_template('/vault/invite.html', id=id, form=form, isAdmin=(subscription.state == 2))

        if not sendInvitation(user, userTo, vault):
            flash('Error')
        return redirect(url_for('vault.showVault', id=id, page=0))
        
    return render_template('/vault/invite.html', id=id, form=form, isAdmin=(subscription.state == 2))
    