import re
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import UserMixin, login_user, login_required, logout_user, current_user

# Import app components
from app import db, jwt, bcrypt, login_manager

# Import module forms
from app.auth.forms import LoginForm

# Importing Schema
from app.schema import User, userstatus

# Defining the blueprint: 'auth', set its url prefix: app.url/auth
auth = Blueprint('auth', __name__, url_prefix='/auth')

# Function to Fetch Next UserID
def getnextid(city):
    lastUser = User.objects(uid__startswith=(str(city)[:3].upper())).order_by('-uid').first()
    if lastUser:
        return int(lastUser['uid'][3:]) + 1
    else:
        return 1

@auth.route('/sign-in/', methods=['GET', 'POST'])
def signin():
    form = LoginForm(request.form)

    if current_user.is_authenticated == True:
        return redirect("/")

    if request.method == 'POST' and form.validate_on_submit():
        if (re.search(r'[A-Za-z]{3}\d*',str(form.loginid.data))):
            checkuser = User.objects(uid=form.loginid.data).first()
        else:
            checkuser = User.objects(mobilenumber=form.loginid.data).first()
        
        if checkuser and bcrypt.check_password_hash(checkuser['password'], form.password.data):
            login_user(checkuser)
            return redirect("/")

        flash("login id / Password Invalid!","error")

    return render_template('auth/sign-in.html', form=form)

# Route for Forgot Password
@auth.route('/forgot-password/', methods=['GET','POST'])
def forgotpassword():
    return render_template("auth/forgot-password.html")

# Route to logout User
@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))

# User Loader for LoginManager
@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()