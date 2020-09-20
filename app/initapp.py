import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import login_required, current_user

# Import app components
from app import db, jwt, bcrypt, login_manager, gst

# Importing Schema
from app.schema import Taxes, Colours, User, Wallet

# Adding Taxes if not exist on init
taxes = [0.00, 5.00, 12.00, 18.00, 28.00]

colours = {"WHITE": "#FFFFFF",
           "SILVER": "#C0C0C0",
           "GRAY": "#808080",
           "BLACK": "#000000",
           "RED": "#FF0000",
           "MAROON": "#800000",
           "YELLOW": "#FFFF00",
           "OLIVE": "#808000",
           "LIME": "#00FF00",
           "GREEN": "#008000",
           "AQUA": "#00FFFF",
           "TEAL": "#008080",
           "BLUE": "#0000FF",
           "NAVY": "#000080",
           "FUCHSIA": "#FF00FF",
           "PURPLE": "#800080"}

if not User.objects(uid="dev"):
    User(
        uid="dev",
        role=128,
        category="individual",
        companyname="",
        fullname="Supreeth Kumar Y P",
        # Password 12345678
        password="$2b$12$/knZ/cknhDjmgklc5v100e.KHvDnaibIfOhYg8CJ3aSeRXVbNcoaC",
        email="supreethkumar.yp@gmail.com",
        mobilenumber="9743977577",
        gstin="",
        communicationaddress="Chitradurga",
        billingaddress="Chitradurga",
        state="Karnataka",
        city="Chitradurga",
        pincode = 577501,
        brand = json.dumps({}),
        openingbalance=0,
        status = 1
    ).save()

for tax in taxes:
    if not Taxes.objects(name="IGST @ %s%s" % (tax, "%")):
        Taxes(
            taxtype="IGST",
            name="IGST @ %s%s" % (tax, "%"),
            percentage=float(tax)
        ).save()

    if not Taxes.objects(name="CGST @ %s%s" % (tax / 2.0, "%")):
        Taxes(
            taxtype="CGST",
            name="CGST @ %s%s" % (tax / 2.0, "%"),
            percentage=float(tax) / 2.0
        ).save()

    if not Taxes.objects(name="SGST @ %s%s" % (tax / 2.0, "%")):
        Taxes(
            taxtype="SGST",
            name="SGST @ %s%s" % (tax / 2.0, "%"),
            percentage=float(tax) / 2.0
        ).save()

if not Taxes.objects(name="Cess @ 2.0%"):
    Taxes(
        taxtype="CESS",
        name="Cess @ 2.0%",
        percentage=2.0
    ).save()

for key, value in colours.items():
    if not Colours.objects(name=key, code=value):
        Colours(
            name=key,
            code=value
        ).save()

if not Wallet.objects(name="sms"):
    Wallet(
        name="sms",
        balance=0
    ).save()

if not Wallet.objects(name="whatsapp"):
    Wallet(
        name="whatsapp",
        balance=0
    ).save()