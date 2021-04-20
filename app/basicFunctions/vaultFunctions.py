from ..models import User, Vault, VaultPayment, VaultSubscription, PaymentState
from ..telegram.telegram import send_message
from .. import db

def createVault(user, vaultName):
    if user.vaultsAmount == 5:
        return False

    vault = Vault(name=vaultName)
    db.session.add(vault)

    subscription = VaultSubscription(user=user, vault=vault, state=2)
    db.session.add(subscription)

    user.vaultsAmount += 1

    db.session.commit()

def sendInvitation(userFrom, userTo, vault):
    subscription = vault.users.filter_by(user_id=userFrom.id).first()

    if subscription is None:
        return False

    if subscription.state != 2:
        return False

    if userTo.vaultsAmount == 5:
        return False
    
    if vault.users.filter_by(user_id=userTo.id).first() is not None:
        return False

    newSubscription = VaultSubscription(user=userTo, vault=vault, state=0)
    db.session.add(newSubscription)
    db.session.commit()

    return True

def confirmInvitation(user, subscription):
    if subscription.user_id != user.id:
        return False

    subscription.state = 1
    user.vaultsAmount += 1
    subscription.vault.usersAmount += 1

    db.session.commit()

    return True

def rejectInvitation(user, subscription):
    if subscription.user_id != user.id:
        return False

    subscription.state = 3

    db.session.commit()

    return True

def confirmPayment(vault, payment, user):
    if payment.vault != vault:
        return False

    state = payment.states.filter_by(user_id=user.id).first()

    if state is not None:
        if state.state == 0 or state.state == 1:
            return False
        return False

    payment.acceptedBy += 1
    if payment.acceptedBy == vault.usersAmount:
        payment.accepted = True
        vault.total += payment.amount

    state = PaymentState(user=user, payment=payment, state=0)
    db.session.add(state)
    db.session.commit()

    return True

def rejectPayment(vault, payment, user):
    if payment.vault != vault:
        return False

    state = payment.states.filter_by(user_id=user.id).first()

    if state is not None:
        if state.state == 0 or state.state == 1:
            return False
        return False

    payment.refused = True
    vault.NotConfirmedTotal -= payment.amount

    state = PaymentState(user=user, payment=payment, state=1)
    db.session.add(state)
    db.session.commit()

    return True
    

def createPayment(vault, userFrom, amount, description):
    if vault.paymentsAmount > 100000:
        return False

    payment = VaultPayment(vault=vault, user=userFrom, amount=amount,\
              about=description, acceptedBy=0, accepted=False)
    
    vault.NotConfirmedTotal += payment.amount
    vault.paymentsAmount += 1

    db.session.add(payment)
    db.session.commit()

    confirmPayment(vault, payment, userFrom)
        
