from . import profile

from ..models import User

from flask import render_template, redirect, url_for, request, flash, make_response
from flask_login import current_user

from ..validators.mainValidators import badUsername

from .forms import UsernameChange, PasswordChange
from wtforms import ValidationError

# Only authorized users can acess this blueprint
@profile.before_request
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

@profile.route('/')
def main():
    return render_template('/profile/main.html')

@profile.route('/stop_telegram')
def stopTelegram():
    user = current_user._get_current_object()
    user.stop_telegram()

    return redirect(url_for('profile.main'))

@profile.route('/help_website')
def helpWebsite():
    flash('Will be soon')
    return redirect(url_for('profile.main'))

@profile.route('/help_telegram')
def helpTelegram():
    flash('Will be soon')
    return redirect(url_for('profile.main'))


@profile.route('/change_username', methods=['GET', 'POST'])
def changeUsername():
    usernameForm = UsernameChange(request.form)

    if request.method == 'POST':
        if usernameForm.validate_on_submit():
            if len(usernameForm.newUsername.data) > 17:
                flash('Your username can\'t be longer 17')
                return render_template('/profile/change-username.html', form=usernameForm)

            if User.query.filter_by(username=str(usernameForm.newUsername.data)).first() is not None:
                flash('This username is used')
                return render_template('/profile/change-username.html', form=usernameForm)

            if not badUsername(usernameForm.newUsername.data):
                usernameForm.newUsername.errors += (ValidationError('Your username has forbidden symbols'),)
                return render_template('/profile/change-username.html', form=usernameForm)

            user = current_user._get_current_object()
            user.username = usernameForm.newUsername.data
               
            return redirect(url_for('profile.main'))

    return render_template('/profile/change-username.html', form=usernameForm)
    
@profile.route('/change_password', methods=['GET', 'POST'])
def changePassword():
    passwordForm = PasswordChange(request.form)

    if request.method == 'POST':
        if passwordForm.validate_on_submit():
            user = current_user._get_current_object()
            user.password = passwordForm.newPassword.data
            
            response = make_response(redirect(url_for('profile.main')))
            response.set_cookie('pver', user.password_ver)

            flash('New password is set')

            return response

    return render_template('/profile/change-password.html', form=passwordForm)
    