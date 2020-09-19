from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, HiddenField
from wtforms_components import ColorField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Email, re
from wtforms.widgets import html5, html_params

from app.schema import Tax_Types, Units

tax_Type_List = [(tax_type, tax_type) for tax_type in Tax_Types]

class TaxForm(FlaskForm):
    taxtype = SelectField("Tax Type", choices=tax_Type_List)
    name = StringField("Tax Name", validators=[InputRequired(message="Please Enter Tax Name")])
    percentage = StringField("Tax Percentage", validators=[InputRequired(message="Please Enter Tax Percentage")])
    
class UnitForm(FlaskForm):
    id = HiddenField("_id", default="")
    code = StringField("Unit Code", validators=[InputRequired(message="Please Enter Unit Code")])
    name = StringField("Unit Name", validators=[InputRequired(message="Please Enter Unit Name")])
    complexflag = BooleanField("Is Complex", default=False)
    factor = StringField("Factor", default=0)
    baseunit = SelectField("Base Unit")

class BrandsForm(FlaskForm):
    id = HiddenField("_id", default="")
    code = StringField("Brand Code", validators=[InputRequired(message="Please Enter Brand Code")])
    name = StringField("Brand Name", validators=[InputRequired(message="Please Enter Brand Name")])

class ProductGroupForm(FlaskForm):
    id = HiddenField("_id", default="")
    code = StringField("Product Group Code", validators=[InputRequired(message="Please Enter Product Group Code")])
    name = StringField("Product Group Name", validators=[InputRequired(message="Please Enter Product Group Name")])

class ProductSubGroupForm(FlaskForm):
    id = HiddenField("_id", default="")
    code = StringField("Product Sub Group Code", validators=[InputRequired(message="Please Enter Product Sub Group Code")])
    name = StringField("Product Sub Group Name", validators=[InputRequired(message="Please Enter Product Sub Group Name")])
    productgroup = SelectField("Product Group")

class ManufacturingProcessForm(FlaskForm):
    id = HiddenField("_id", default="")
    code = StringField("Product Group Code", validators=[InputRequired(message="Please Enter Product Group Code")])
    name = StringField("Product Group Name", validators=[InputRequired(message="Please Enter Product Group Name")])

class UserGroupsForm(FlaskForm):
    id = HiddenField("_id", default="")
    name = StringField("User Group Name", validators=[InputRequired(message="Please Enter User Group Name")])
    branch = SelectField("Branch", validators=[InputRequired(message="Please Select Branch")])

class Colour1Form(FlaskForm):
    id = HiddenField("_id", default="")
    name = StringField("Colour Name", validators=[InputRequired(message="Please Enter Colour Name")])
    code = StringField("Pick a Colour", validators=[InputRequired(message="Please Enter Colour Name")])