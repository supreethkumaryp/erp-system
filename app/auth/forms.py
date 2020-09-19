from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Email
from wtforms.widgets import html5

class LoginForm(FlaskForm):
    loginid = StringField("loginid", validators=[InputRequired(message="Please Enter loginid / Email")])
    password = PasswordField("password", validators=[InputRequired("Please Enter Password"), Length(min=8, message="Password Too short: Minimum of '8' characters")])
    