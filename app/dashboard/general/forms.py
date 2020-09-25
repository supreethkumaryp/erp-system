import datetime
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, HiddenField, DateTimeField, RadioField, FileField, FieldList, FormField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Email
from wtforms.widgets import html5, html_params
from flask_wtf.file import FileAllowed

from app.schema import userstatus, roles, Product_Type, Product_Unit, Product_Price_Type, Discount_Type, Brands, Colours, userClass

statuschoice = [(str(value),key.replace("_"," ").capitalize()) for key,value in userstatus.items()]
roleschoice = [(str(value),key.replace("_"," ").capitalize()) for key,value in roles.items() if key != "developer"]
userclasschoice = [(str(value),key.replace("_"," ")) for key,value in userClass.items()]
producttypechoice = [(ptype.lower(),ptype) for ptype in Product_Type]
productunitchoice = [(key,value) for key,value in Product_Unit.items()]
productpricetypechoice = [(key,value) for key,value in Product_Price_Type.items()]
discounttypechoice = [(key,value) for key,value in Discount_Type.items()]

class BranchForm(FlaskForm):
    id = HiddenField("_id",default="")
    code = StringField("Branch Code", validators=[InputRequired(message="Please Enter Branch Code")])
    name = StringField("Branch Name", validators=[InputRequired(message="Please Enter Branch Name")])
    gstregtype = SelectField("GST Registration Type", choices=[('registered','Registered'),('composition','Composition'),('notregistered','Not Registered')])
    gstin = StringField("GSTIN")
    phonenumber = StringField("Phone Numbers")
    email = StringField("Email")
    address = TextAreaField("Address", validators=[InputRequired(message="Please Enter Address")])
    state = StringField("State", validators=[InputRequired(message="Please Enter State")], render_kw={"readonly":True})
    city = StringField("City", validators=[InputRequired(message="Please Enter City")], render_kw={"readonly":True})
    pincode = IntegerField("Pincode", validators=[InputRequired("Please Enter Pincode")], widget=html5.NumberInput())

class PartyForm(FlaskForm):
    id = HiddenField("_id",default="")
    role = SelectField("User Role", choices=roleschoice, default=1)
    branch = SelectField("Branch")
    category = RadioField('User Catagory', choices=[('individual','Individual'),('company','Company')], validators=[InputRequired(message="Please Select User Catagory")], default='individual')
    group = SelectField("User Group")
    companyname = StringField("Company Name")
    fullname = StringField("Full Name", validators=[InputRequired(message="Please Enter Full name")])
    email = StringField("Email")
    mobilenumber = StringField("Mobile Number", validators=([InputRequired(message="Please Enter Valid Mobile Number")]))
    whatsapp = BooleanField("Send Msg in Whatsapp")
    gstin = StringField("GSTIN")
    billingaddress = TextAreaField("Address", validators=[InputRequired(message="Please Enter Address")])
    city = StringField("City", validators=[InputRequired(message="Please Enter City")])
    state = StringField("State", validators=[InputRequired(message="Please Enter State")])
    pincode = IntegerField("Pincode", validators=([InputRequired("Please Enter Pincode")]), widget=html5.NumberInput())
    # brand = StringField("Brand Label")
    userclass = SelectField("User Class", choices=userclasschoice, default=userClass['Class_C'])
    openingbalance = StringField("Opening Balance")
    openingbalancedate = StringField("Opening Balance Date", default=datetime.date.today().strftime("%d/%m/%Y"))
    status = SelectField("User Status", choices=statuschoice, default=1)

class DesignForm(FlaskForm):
    designid = HiddenField("_id", default="")
    designname = StringField(label="Design Name")
    colour = SelectMultipleField(label="Colour", render_kw={"data-placeholder":"Select a Colour..."})
    photo = FileField('image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')], render_kw={"accept":"image/x-png,image/jpeg"})

class ProductForm(FlaskForm):
    id = HiddenField("_id",default="")
    producttype = SelectField(label="Product Type",choices=producttypechoice)
    code = StringField(label="HSN Code")
    barcode = StringField(label="Barcode")
    name = StringField(label="Product Name")
    brand = SelectField(label="Brand")
    group = SelectField(label="Product Group")
    subgroup = SelectField(label="Product Subgroup")
    tax = SelectField(label="Tax Percentage")
    cess = SelectField(label="Cess")
    minstock = StringField(label="Minimum Stock", default=0)
    unitofmeasure = SelectField(label="Unit of Measure")
    length = StringField(label="Length")
    width = StringField(label="Width")
    unit = SelectField(label="Unit", choices=productunitchoice)
    sellingprice = StringField(label="Selling Price")
    costprice = StringField(label="Cost Price")
    discountprice = StringField(label="Discount")
    sellingpricetype = SelectField(label="Selling Price Type", choices=productpricetypechoice)
    costpricetype = SelectField(label="Cost Price Type", choices=productpricetypechoice)
    discounttype = SelectField(label="Discount Type", choices=discounttypechoice)
    designs = FieldList(FormField(DesignForm), min_entries=1)
    productclass = SelectField("Product Class", choices=userclasschoice, default=userClass['Class_C'])
    addDesign = SubmitField(label="Add Design")
    removeDesign = SubmitField(label="Remove Design")