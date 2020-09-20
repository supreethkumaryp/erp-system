from datetime import datetime
from pytz import timezone
from app import db
from flask_login import UserMixin
from mongoengine import StringField, IntField, BooleanField, EmailField, UUIDField, IntField, DateTimeField, FloatField, ListField, ReferenceField, CASCADE, NULLIFY
import mongoengine_goodjson as gj

roles = {
    "party" : 1,
    "collection_boy" : 2,
    "spl_party" : 4,
    "operator" : 8,
    "merchant" : 16,
    "admin" : 32,
    "super_admin" : 64,
    "developer" : 128
}

userstatus = {
    "unverified": 0,
    "verified": 1,
    "vip": 2,
    "locked": 4,
    "deleted": 8
}

Tax_Types = ['CGST', 'SGST', 'IGST', 'Cess', 'Composition', 'VAT']

Product_Type = ['Goods','Service']

Product_Unit = {
    'in' : 'Inches',
    'ft' : 'Feets'
}

Product_Price_Type = {
    'excluding' : 'Excluding Tax',
    'including' : 'Including Tax'
}

Discount_Type = {
    'rupees' : 'Rs',
    'percentage' : '%'
}

class Branches(db.Document):
    meta = {"collection": "branches"}
    code = StringField()
    name = StringField()
    gstregtype = StringField()
    gstin = StringField()
    phonenumber = ListField()
    email = EmailField()
    address = StringField()
    state = StringField()
    city = StringField()
    pincode = IntField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class User_Groups(gj.Document):
    meta = {"collection":"user_groups"}
    name = StringField()
    branch = ReferenceField(Branches, dbref=True, reverse_delete_rule=CASCADE)
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Colours(gj.Document):
    meta = {"collection":"colours"}
    name = StringField()
    code = StringField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class User(UserMixin, gj.Document):
    meta = {"collection": "users"}
    uid = StringField()
    role = IntField(default=roles['party'])
    branch = ReferenceField(Branches, dbref=True, reverse_delete_rule=NULLIFY)
    category = StringField()
    group = ReferenceField(User_Groups, dbref=True, reverse_delete_rule=NULLIFY)
    companyname = StringField(default="None")
    fullname = StringField()
    password = StringField()
    email = EmailField()
    mobilenumber = StringField()
    whatsapp = BooleanField()
    gstin = StringField(default="None")
    communicationaddress = StringField()
    billingaddress = StringField()
    state = StringField()
    city = StringField()
    pincode = IntField()
    brand = StringField()
    registerasmerchant = BooleanField(default=False)
    openingbalance = FloatField(default=0.00)
    openingbalancedate = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))
    status = IntField(default=userstatus['unverified'])
    otp = StringField(default=None)
    otp_sent_time = StringField(default=None)
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Units(gj.Document):
    meta = {"collection":"units"}
    code = StringField()
    name = StringField()
    complexflag = BooleanField(default=False)
    factor = FloatField()
    baseunit = ReferenceField("self", dbref=True,reverse_delete_rule=CASCADE)
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Taxes(db.Document):
    meta = {"collection":"taxes"}
    taxtype = StringField()
    name = StringField()
    percentage = FloatField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Manufacturing_Process(db.Document):
    meta = {"collection":"manufacturing_process"}
    code = StringField()
    name = StringField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Brands(db.Document):
    meta = {"collection":"brands"}
    code = StringField()
    name = StringField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Product_Groups(db.Document):
    meta = {"collection":"product_groups"}
    code = StringField()
    name = StringField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Product_Sub_Groups(gj.Document):
    meta = {"collection":"product_sub_groups"}
    code = StringField()
    name = StringField()
    productgroup = ReferenceField(Product_Groups, dbref=True, reverse_delete_rule=CASCADE)
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class ProductDesign(gj.Document):
    meta = {"collection":"productdesign"}
    code = StringField()
    colour = ListField()
    photo = StringField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Products(gj.Document):
    meta = {"collection":"products"}
    producttype = StringField()
    code = StringField()
    barcode = StringField()
    name = StringField()
    brand = ReferenceField(Brands, dbref=True, reverse_delete_rule=NULLIFY)
    group = ReferenceField(Product_Groups, dbref=True, reverse_delete_rule=NULLIFY)
    subgroup = ReferenceField(Product_Sub_Groups, dbref=True, reverse_delete_rule=NULLIFY)
    tax = ReferenceField(Taxes, dbref=True, reverse_delete_rule=NULLIFY)
    cess = ReferenceField(Taxes, dbref=True, reverse_delete_rule=NULLIFY)
    unitofmeasure = ReferenceField(Units, dbref=True, reverse_delete_rule=NULLIFY)
    length = FloatField(default=0.0)
    width = FloatField(default=0.0)
    unit = StringField()
    sellingprice = FloatField()
    minstock = IntField(default=0)
    costprice = FloatField()
    discountprice = FloatField()
    sellingpricetype = StringField()
    costpricetype = StringField()
    discounttype = StringField()
    # photos = ListField()
    productdesign = ListField(field=ReferenceField(ProductDesign, dbref=True, reverse_delete_rule=NULLIFY))
    stock = IntField(default=0)
    status = BooleanField()
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))

class Wallet(db.Document):
    meta = {"collection":"wallet"}
    name = StringField()
    balance = IntField(default=0)
    created_at = StringField(default=str(datetime.now(timezone('Asia/Kolkata')).timestamp()))