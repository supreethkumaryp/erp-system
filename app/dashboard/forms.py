import datetime
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, HiddenField, DateTimeField, RadioField, PasswordField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Email
from wtforms.widgets import html5, html_params

from app.schema import userstatus, roles

class EditUserInfoForm(FlaskForm):
    uid = StringField("Login Id", render_kw={"readonly":True})
    category = RadioField('User Catagory', choices=[('individual','Individual'),('company','Company')], validators=[InputRequired(message="Please Select User Catagory")], default='individual')
    companyname = StringField("Company Name")
    fullname = StringField("Full Name", validators=[InputRequired(message="Please Enter Full name")])
    email = StringField("Email")
    mobilenumber = StringField("Mobile Number", validators=([InputRequired(message="Please Enter Valid Mobile Number")]))
    whatsapp = BooleanField("Send Msg in Whatsapp")
    brand = StringField("Brand Label")
    gstin = StringField("GSTIN")
    communicationaddress = TextAreaField("Communication Address", validators=[InputRequired(message="Please Enter Address")])
    samebilladdress = BooleanField("Same As Billing Address")
    billingaddress = TextAreaField("Billing Address", validators=[InputRequired(message="Please Enter Address")])
    city = StringField("City", validators=[InputRequired(message="Please Enter City")], render_kw={"readonly":True})
    state = StringField("State", validators=[InputRequired(message="Please Enter State")], render_kw={"readonly":True})
    pincode = IntegerField("Pincode", validators=([InputRequired("Please Enter Pincode")]), widget=html5.NumberInput())
    submituserinfo = SubmitField("Save Changes")

class EditUserPasswordForm(FlaskForm):
    oldpassword = PasswordField("Old Password", validators=([InputRequired("Please Enter Old Password")]))
    newpassword = PasswordField("New Password", validators=([InputRequired("Please Enter New Password")]))
    retypenewpassword = PasswordField("Retype New Password", validators=([InputRequired("Please Enter New Password")]))
    submituserpassword = SubmitField("Save Changes")