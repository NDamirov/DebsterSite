from . import auth
from .forms import *
from flask import render_template, redirect, url_for, request, flash, make_response
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User
from ..email.email import *
from .. import db

import requests
from random import randint

from wtforms import ValidationError
from ..validators.mainValidators import badUsername

# Login/Register page
@auth.route('/', methods=['GET', 'POST'])
def main():
    if current_user.is_authenticated and current_user.confirmedAccount:
        return redirect(url_for('main.main_route'))
        
    loginForm = LoginForm(request.form)
    registerForm = RegisterForm(request.form)

    if request.method == 'POST':
        if loginForm.log.data and loginForm.validate():

            if len(loginForm.emailLog.data) > 100 or len(loginForm.password.data) > 100:
                loginForm.emailLog.errors += (ValidationError('Username or password is incorrect'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)
            
            users = db.session.execute('SELECT * FROM users WHERE email=:email', {'email': str(loginForm.emailLog.data)}).fetchall()

            if len(users) == 0:
                loginForm.emailLog.errors += (ValidationError('Username or password is incorrect'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)


            user = User.query.get(users[0]['id'])

            if user is None or not user.verify_password(str(loginForm.password.data)):
                loginForm.emailLog.errors += (ValidationError('Username or password is incorrect'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            login_user(user)

            if not user.confirmedAccount:
                response = make_response(redirect(url_for('auth.confirm')))
                response.set_cookie('pver', user.password_ver)
                return response

            response = make_response(redirect(url_for('main.main_route')))
            response.set_cookie('pver', user.password_ver)

            return response
            

        if registerForm.register.data and registerForm.validate():
            if len(registerForm.email.data) > 100:
                registerForm.email.errors += (ValidationError('Your email can\'t be longer 100'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            if User.query.filter_by(email=registerForm.email.data).first() is not None:
                registerForm.email.errors += (ValidationError('This email is already used'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            if len(registerForm.newUsername.data) > 17:
                registerForm.newUsername.errors += (ValidationError('Your username can\'t be longer 17'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            if not badUsername(registerForm.newUsername.data):
                registerForm.newUsername.errors += (ValidationError('Your username has forbidden symbols'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            if User.query.filter_by(username=registerForm.newUsername.data).first() is not None:
                registerForm.newUsername.errors += (ValidationError('This username is already used'),)
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

            if registerForm.password.data != registerForm.passwordCopy.data:
                return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)
                
            user = User(email=registerForm.email.data, \
                        username=registerForm.newUsername.data, \
                        password=registerForm.password.data)
            
            db.session.add(user)
            db.session.commit()

            response = make_response(redirect(url_for('auth.confirm')))
            response.set_cookie(user.password_ver)
            login_user(user)

            token = user.generate_confirmation_token().decode('utf-8')
            send_mail(user.email, 'Confirm', 'email/confirm', user=user, token=token)

            return response


    return render_template('/auth/main.html', loginForm=loginForm, registerForm=registerForm)

# Url for logging out
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.main'))

# Page for confirmation after user've registered
@auth.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if not current_user.is_authenticated or current_user._get_current_object().confirmedAccount:
        return redirect(url_for('auth.main'))

    confirm = ConfirmForm()

    if request.method == 'POST':
        token = confirm.token.data
        if current_user.confirm(token):
            return redirect(url_for('main.main_route'))
        else:
            flash('Error: invalid token')
            return redirect(url_for('auth.confirm'))
    
    return render_template('/auth/confirm.html', confirmForm=confirm)

# Password recovering page
@auth.route('/recovery', methods=['POST', 'GET'])
def recovery():
    if current_user.is_authenticated:
        return redirect(url_for('main.main_route'))

    recoveryForm = RecoveryForm()
    
    if request.method == 'POST':
        user = User.query.filter_by(email=recoveryForm.email.data).first()
        if user is None:
            flash('Incorrect email or username')
            return redirect(url_for('auth.recovery'))

        if user.username != str(recoveryForm.userName.data):
            flash('Incorrect email or username')
            return redirect(url_for('auth.recovery'))

        token = user.generate_recovery_token()

        send_mail(user.email, 'Recovery', '/email/recover', user=user, token=token)

        flash('We\'ve sent an email')
        return redirect(url_for('auth.main'))

    return render_template('/auth/recovery.html', form = recoveryForm)

# Final part of recovering
# New password is created
@auth.route('/recover/<token>', methods=['POST', 'GET'])
def recover(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.main_route'))

    form = PasswordEditForm()

    if request.method == 'POST' and form.validate():
        if not User.change_password(token, str(form.password.data)):
            flash('Invalid token')
        else:
            flash('Password was changed')
        return redirect(url_for('auth.main'))
    
    return render_template('/auth/recover.html', form=form, token=token)


# OAuth
@auth.route('/oauth/vk')
def oauth_begin():
    return redirect('https://oauth.vk.com/authorize?client_id={}&redirect_uri=https://debster.me/authorize/oauth/continue&display=popup&scope=4194304&response_type=code'.format(7583394))

@auth.route('/oauth/continue')
def oauth_continue():
    try:
        code = request.args.get('code')
    except:
        flash('Error')
        return redirect(url_for('auth.main'))

    url = 'https://oauth.vk.com/access_token?client_id={}&client_secret={}&redirect_uri=https://debster.me/authorize/oauth/continue&code={}'.format(7583394, '4nY843VZg0NwbZoSMYCQ', str(code))

    req = requests.get(url=url)

    data = req.json()


    try:
        email = data['email']
        user_id = data['user_id']
    except:
        flash('User must have email')
        return redirect(url_for('auth.main'))

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email,\
                    usingOAuth=True,\
                    user_id=user_id, \
                    confirmedAccount=True)
        db.session.add(user)
        db.session.commit()

        user.username = 'id' + str(user.id)
        password = ''.join(chr(ord('a') + randint(0, 25)) for i in range(10))
        user.password = password

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Change your password and username')

        response = make_response(redirect(url_for('profile.main')))
        response.set_cookie('pver', user.password_ver)

        return response


    if user.usingOAuth and user.user_id == user_id:
        login_user(user)

        response = make_response(redirect(url_for('auth.main')))
        response.set_cookie('pver', user.password_ver)

        return response
    
    flash('This email is already used')

    
    return redirect(url_for('auth.main'))