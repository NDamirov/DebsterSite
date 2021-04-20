from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, logout_user
from .forms import DebtConfirmation, CreateDebt
from ..models import Debt, User
from ..basicFunctions.mainFunctions import *
from ..validators.mainValidators import pure
from . import main

from wtforms import ValidationError
import datetime

# Only authorized users can access this Blueprint
@main.before_request
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

# Main page: last 20 debts + totalDebt
# TODO: In rows 19, 20 change a lot of filter_by with one request
@main.route('/')
def main_route():
    user = current_user._get_current_object()
    gave = user.give.order_by(Debt.id.desc()).filter_by(confirmed=True).filter_by(refused=False).filter_by(paid=False).limit(15).all()
    ret = user.ret.order_by(Debt.id.desc()).filter_by(confirmed=True).filter_by(refused=False).filter_by(paid=False).limit(15).all()

    debts = []
    for debt in gave:
        debts.append([-debt.id, debt.total, debt.ret.username, debt.about])

    for debt in ret:
        debts.append([-debt.id, -debt.total, debt.give.username, debt.about])

    debts.sort()
    
    if len(debts) > 15:
        debts = debts[:15]

    #TODO: Not use sort. Go throw gave and ret at the same time
    
    return render_template('main/main.html', totalDebt=user.totalDebt, debts=debts,
     notConfirmedTotalDebt=user.notConfirmedTotalDebt)

# Page which displays debt for confirmation
@main.route('/confirm/<page>')
def confirm(page = 0):
    user = current_user._get_current_object()

    try:
        page = int(page)
    except:
        return redirect(url_for('main.confirm', page=0))

    if page < 0:
        return redirect(url_for('main.confirm', page=0))

    if page != 0 and (page - 1) * 15 >= user.notConfirmedAmount:
        return redirect(url_for('main.confirm', page=0))

    debts = user.ret.filter_by(confirmed=False).order_by(Debt.id.desc()) \
            .limit(15).offset(page * 15).all()
    
    return render_template('/main/confirm.html', debts=debts, page=page)

# Page for confirmation debt
@main.route('/confirm_debt/<int:id>')
def confirm_debt(id):
    debt = Debt.query.get(id)
    user = current_user._get_current_object()
    
    if not debt:
        flash('Error: no debt found')
        return redirect(url_for('main.confirm', page=0))

    if not confirmDebt(user, debt):
        flash('Error: can\'t confirm debt')
        return redirect(url_for('main.confirm', page=0))
    
    return redirect(url_for('main.confirm', page=0))
    
# Page for rejecting debt
@main.route('/reject_debt/<int:id>')
def reject_debt(id):
    debt = Debt.query.get(id)
    user = current_user._get_current_object()
    
    if not debt:
        flash('Error: no debt found')
        return redirect(url_for('main.confirm', page=0))

    if not rejectDebt(user, debt):
        flash('Error: can\'t reject debt')
        return redirect(url_for('main.confirm', page=0))
    
    return redirect(url_for('main.confirm', page=0))

@main.route('/pay_debt/<int:id>')
def pay_debt(id):
    debt = Debt.query.get(id)
    user = current_user._get_current_object()

    if not debt:
        flash('Error: no debt found')
        return redirect(url_for('main.lended', page=0))

    if not payDebt(user, debt):
        flash('Error: can\'t reject debt')
        return redirect(url_for('main.lended', page=0))

    return redirect(url_for('main.lended', page=0))

# Page for creating debt
@main.route('/give', methods=['GET', 'POST'])
def create():
    createForm = CreateDebt(request.form)

    if request.method == 'POST' and createForm.validate():

        if len(createForm.debtTo.data) > 17:
            createForm.debtTo.errors += (ValidationError("No user with this username"),)
            return render_template('/main/create.html', form=createForm)

        if len(createForm.description.data) > 150:
            createForm.description.errors += (ValidationError("Your description is longer 150"))
            return render_template('/main/create.html', form=createForm)

        user = current_user._get_current_object()
        userTo = User.query.filter_by(username=str(createForm.debtTo.data)).first()
        if not userTo:
            createForm.debtTo.errors += (ValidationError("No user with this username"),)
            return render_template('/main/create.html', form=createForm)

        if user == userTo:
            createForm.debtTo.errors += (ValidationError("You can't lend yourself"),)
            return render_template('/main/create.html', form=createForm)

        if user.debtsLeft == 0:
            flash("You have too many debts")
            return render_template('/main/create.html', form=createForm)


        total = int(createForm.total.data)

        if total <= 0:
            createForm.total.errors += (ValidationError("You can't lend < 0"),)
            return render_template('/main/create.html', form=createForm)

        description = pure(str(createForm.description.data))

        createDebt(user, userTo, total, description)

        return redirect(url_for('main.main_route'))

    return render_template('/main/create.html', form=createForm)

# Page for taking money
@main.route('/take', methods=['POST', 'GET'])
def take():
    createForm = CreateDebt(request.form)

    if request.method == 'POST' and createForm.validate():

        if len(createForm.debtTo.data) > 17:
            createForm.debtTo.errors += (ValidationError("No user with this username"),)
            return render_template('/main/create.html', form=createForm)

        if len(createForm.description.data) > 150:
            createForm.description.errors += (ValidationError("Your description is longer 150"))
            return render_template('/main/create.html', form=createForm)

        user = current_user._get_current_object()
        userFrom = User.query.filter_by(username=str(createForm.debtTo.data)).first()
        if not userFrom:
            createForm.debtTo.errors += (ValidationError("No user with this username"),)
            return render_template('/main/create.html', form=createForm)

        if user == userFrom:
            createForm.debtTo.errors += (ValidationError("You can't lend yourself"),)
            return render_template('/main/create.html', form=createForm)

        if userFrom.debtsLeft == 0:
            flash("You have too many debts")
            return render_template('/main/create.html', form=createForm)


        total = int(createForm.total.data)

        if total <= 0:
            createForm.total.errors += (ValidationError("You can't lend < 0"),)
            return render_template('/main/create.html', form=createForm)

        description = pure(str(createForm.description.data))

        createDebt(userFrom, user, total, description, isConfirmed=True)

        return redirect(url_for('main.main_route'))

    return render_template('/main/create.html', form=createForm)

# Page for given money
@main.route('/lended/<page>', methods=['GET', 'POST'])
def lended(page = 0):
    user = current_user._get_current_object()

    try:
        page = int(page)
    except:
        return redirect(url_for('main.lended', page=0))

    if page < 0:
        return redirect(url_for('main.lended', page=0))
    
    if page != 0 and (page - 1) * 15 >= user.giveAmount:
        return redirect(url_for('main.lended', page=0))
    

    gave = user.give.order_by(Debt.id.desc()).limit(15).offset(15 * page).all()

    return render_template('/main/lended.html', gave=gave, page=page)


# Page for taken money
@main.route('/borrowed/<page>', methods=['GET', 'POST'])
def borrowed(page = 0):
    user = current_user._get_current_object()

    try:
        page = int(page)
    except:
        return redirect(url_for('main.borrowed', page=0))

    if page < 0:
        return redirect(url_for('main.borrowed', page=0))

    if page != 0 and (page - 1) * 15 >= user.retAmount:
        return redirect(url_for('main.borrowed', page=0))

    ret = user.ret.order_by(Debt.id.desc()).offset(15 * page).limit(15).all()

    return render_template('/main/borrowed.html', ret=ret, page=page)