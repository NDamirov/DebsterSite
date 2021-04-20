from ..models import User, Debt
from ..telegram.telegram import send_message
from .. import db

# 'userFrom' lented money 'userTo' 'debtWeight'
def createDebt(userFrom, userTo, debtWeight, description, isConfirmed=False):
    debt = Debt(about=description, give=userFrom, ret=userTo, total=debtWeight, \
                confirmed=isConfirmed)

    userFrom.notConfirmedTotalDebt += debtWeight
    userTo.notConfirmedTotalDebt -= debtWeight

    userFrom.debtsLeft -= 1

    userFrom.giveAmount += 1
    userTo.retAmount += 1

    if not isConfirmed:
        userTo.notConfirmedAmount += 1
    else:
        userTo.totalDebt -= debtWeight
        userFrom.totalDebt += debtWeight


    db.session.add(debt)
    db.session.commit()

    if not isConfirmed:
        send_message(userTo, debt, 'New debt.')
    else:
        send_message(userFrom, debt, 'New debt.')
    return True

# 'user' confirmed 'debt'
def confirmDebt(user, debt):
    if debt.ret != user or debt.confirmed:
        return False
    
    debt.give.totalDebt += debt.total
    debt.ret.totalDebt -= debt.total

    debt.confirmed = 1

    user.notConfirmedAmount -= 1

    db.session.commit()

    send_message(debt.give, debt, 'Debt is confirmed.')

    return True

# 'user' refused 'debt'
def rejectDebt(user, debt):
    if debt.ret != user or debt.confirmed:
        return False

    debt.give.notConfirmedTotalDebt -= debt.total
    debt.ret.notConfirmedTotalDebt += debt.total

    debt.confirmed = 1
    debt.refused = 1

    user.notConfirmedAmount -= 1

    db.session.commit()

    send_message(debt.give, debt, 'Debt is rejected.')

    return True

# 'user' confirmed that 'debt' was paid
def payDebt(user, debt):
    if debt.give != user or debt.paid or debt.refused or not debt.confirmed:
        return False

    debt.give.notConfirmedTotalDebt -= debt.total
    debt.ret.notConfirmedTotalDebt += debt.total

    debt.give.totalDebt -= debt.total
    debt.ret.totalDebt += debt.total

    debt.paid = True

    db.session.commit()

    send_message(debt.ret, debt, 'Debt is paid.')

    return True

    