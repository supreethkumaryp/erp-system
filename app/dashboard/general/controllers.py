import json, os
import string
import time
from random import choice
from datetime import datetime
from pytz import timezone
from wtforms import StringField
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from config import BASE_DIR

# Import app components
from app import db, jwt, bcrypt, login_manager, gst#, dropzone

# Import module forms
from app.dashboard.general.forms import BranchForm, PartyForm, ProductForm

# Importing Schema
from app.schema import Branches, User, roles, userstatus, User_Groups, Products, Brands, Product_Groups, Product_Sub_Groups, Taxes, Units, Products

# Importing User UID generator
from app.auth.controller import getnextid

# Importing API's
from app.api.controller import sendSMS, checkSMSBalance

general = Blueprint('general', __name__, url_prefix='/dashboard')

def generate_password(length):
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(length))

# def get_new_barcode():
#     while True:
#         barcode = str(int(round(time.time() * 1000)))
#         if not Products.objects(barcode=barcode):
#             return barcode

@general.route('/branches/', methods=['GET', 'POST'])
@login_required
def branches():
    branches = Branches.objects()
    form = BranchForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():

        if (form.gstregtype.data != "notregistered" and form.gstin.data == ""):
            flash("For "+form.gstregtype.data+" GSTIN is Required", "error")
            return render_template('dashboard/general/branches.html', branches=branches, form=form)

        if form.gstin.data != "":
            # Validate GST Number Pattern.
            if (not gst.checkpattern(form.gstin.data)):
                flash("Invalid GST Pattern!", "error")
                return render_template('dashboard/general/branches.html', branches=branches, form=form)

            # Validate GST Number Checksum.
            if (not gst.checkchecksum(form.gstin.data)):
                flash("Invalid GST Number!", "error")
                return render_template('dashboard/general/branches.html', branches=branches, form=form)
            
        if(form.id.data == ""):
            checkbranch = Branches.objects(code=form.code.data).first()

            if checkbranch:
                flash("Branch Code Already Exist!", "error")
                return render_template('dashboard/general/branches.html', branches=branches, form=form)

            branch = Branches(
                code = form.code.data,
                name = form.name.data,
                gstregtype = form.gstregtype.data,
                gstin = form.gstin.data,
                phonenumber = [x.strip() for x in form.phonenumber.data.split(",")],
                email = form.email.data,
                address = form.address.data,
                state = form.state.data,
                city = form.city.data,
                pincode = form.pincode.data
            ).save()
            flash("Added New Branch","success")
        else:
            branch = Branches(pk=form.id.data).update(
                code = form.code.data,
                name = form.name.data,
                gstregtype = form.gstregtype.data,
                gstin = form.gstin.data,
                phonenumber = [x.strip() for x in form.phonenumber.data.split(",")],
                email = form.email.data,
                address = form.address.data,
                state = form.state.data,
                city = form.city.data,
                pincode = form.pincode.data
            )
            flash("Updated Branch","success")
        return redirect(url_for('general.branches'))
    return render_template('dashboard/general/branches.html', branches=branches, form=form)

@general.route('/get-branch-details/', methods=['GET', 'POST'])
@login_required
def getbranchdetails():
    branch = Branches.objects(code=request.form["code"]).first()
    if branch:
        return jsonify(
            id = str(branch.pk),
            code = branch.code,
            name = branch.name,
            gstregtype = branch.gstregtype,
            gstin = branch.gstin,
            phonenumber = ", ".join(branch.phonenumber),
            email = branch.email,
            address = branch.address,
            state = branch.state,
            city = branch.city,
            pincode = branch.pincode
        )
    else:
        return jsonify(status="error")

@general.route('/parties/', methods=['GET', 'POST'])
@login_required
def parties():
    brands_data = ["label_" + str(brand.name).replace(" ","_").strip() for brand in Brands.objects()]

    for key in brands_data:
        setattr(PartyForm, key, StringField(key))

    form = PartyForm(request.form)
    form.branch.choices = [("", "Select Branch")] + [(str(branch.pk), branch.code) for branch in Branches.objects()]
    form.group.choices = [("", "Select Group")] + [(str(group.pk), group.name) for group in User_Groups.objects()]
    
    if request.method == 'POST' and form.validate_on_submit():
        if form.gstin.data != "":
            # Validate GST Number Pattern.
            if (not gst.checkpattern(form.gstin.data)):
                flash("Invalid GST Pattern!", "error")
                return redirect(url_for('general.parties'))

            # Validate GST Number Checksum.
            if (not gst.checkchecksum(form.gstin.data)):
                flash("Invalid GST Number!", "error")
                return redirect(url_for('general.parties'))

        if form.id.data == "new":
            existing_user = User.objects(mobilenumber=form.mobilenumber.data).first()

            if existing_user is None:

                if not checkSMSBalance(mode="sms"):
                    flash("SMS Limit Exceeded", "error")
                    return redirect(url_for('general.parties'))

                password = generate_password(8)
                temp_labels = {}
                for key in form.data.items():
                    if key[0].startswith('label_'):
                        temp_labels[key[0]] = key[1] if key[1] else "NA"
                uid = str(form.city.data)[0:3].upper() + str(getnextid(form.city.data))
                user = User(
                    uid = uid,
                    role = int(form.role.data),
                    branch = Branches.objects(pk=form.branch.data).first().to_dbref() if form.branch.data else None,
                    category = form.category.data,
                    group = User_Groups.objects(pk=form.group.data).first().to_dbref() if form.group.data else None,
                    companyname = form.companyname.data,
                    fullname = form.fullname.data,
                    password = bcrypt.generate_password_hash(password),
                    email = form.email.data if form.email.data else None,
                    mobilenumber = form.mobilenumber.data,
                    whatsapp = form.whatsapp.data,
                    gstin = form.gstin.data,
                    communicationaddress = form.billingaddress.data,
                    billingaddress = form.billingaddress.data,
                    brand = json.dumps(temp_labels),
                    state = form.state.data,
                    city = form.city.data,
                    pincode = form.pincode.data,
                    openingbalance = form.openingbalance.data if form.openingbalance.data else 0,
                    openingbalancedate = str(datetime.strptime(form.openingbalancedate.data, "%d/%m/%Y").timestamp()),
                    status = int(form.status.data)
                ).save()

                if user:
                    MSG = "Hey {}, Welcome to Paras Doors.\r\nFrom now you can login to www.parasdoors.com using\r\nLogin ID: {} / {},\r\nPassword: {}".format(form.fullname.data, uid, form.mobilenumber.data, password)
                    status = sendSMS(mobileNumber=form.mobilenumber.data, MSG=MSG, mode="sms")
                    if not status:
                        flash("Failed to Send SMS to User", "error")
                    flash("New User Added Successfully", "success")
                    return redirect(url_for('general.parties'))
                
                flash("Failed to Create User", "error")
                return redirect(url_for('general.parties'))

            flash("User Already Exists!", "error")
            return redirect(url_for('general.parties'))

        else:
            temp_labels = {}
            for key in form.data.items():
                if key[0].startswith('label_'):
                    temp_labels[key[0]] = key[1] if key[1] else "NA"
            existing_user = User.objects(mobilenumber=form.mobilenumber.data).first()
            if (existing_user is None) or (str(existing_user['id']) == form.id.data):
                user = User(pk=form.id.data).update(
                    role = int(form.role.data),
                    branch = Branches.objects(pk=form.branch.data).first().to_dbref() if form.branch.data else None,
                    category = form.category.data,
                    group = User_Groups.objects(pk=form.group.data).first().to_dbref() if form.group.data else None,
                    companyname = form.companyname.data if form.category.data == "company" else "",
                    fullname = form.fullname.data,
                    email = form.email.data if form.email.data else None,
                    mobilenumber = form.mobilenumber.data,
                    whatsapp = form.whatsapp.data,
                    gstin = form.gstin.data,
                    communicationaddress = form.billingaddress.data,
                    billingaddress = form.billingaddress.data,
                    state = form.state.data,
                    city = form.city.data,
                    pincode = form.pincode.data,
                    brand = json.dumps(temp_labels),
                    openingbalance = form.openingbalance.data,
                    openingbalancedate = str(datetime.strptime(form.openingbalancedate.data, "%d/%m/%Y").timestamp()),
                    status = int(form.status.data)
                )

                if user:
                    flash("Updated User Successfully", "success")
                    return redirect(url_for('general.parties'))

                flash("Failed to Create User", "error")
                return redirect(url_for('general.parties'))
            
            flash("Mobile Number Already Exist", "error")
            return redirect(url_for('general.parties'))

    return render_template('dashboard/general/parties.html', form=form, brands_data=brands_data)

@general.route('/get-all-parties/', methods=['GET', 'POST'])
@login_required
def getallparties():
    users = User.objects(role__lte=current_user.role, status__ne=userstatus['deleted'], pk__ne=current_user.pk).only('uid','fullname','mobilenumber','gstin','openingbalance','category','role','status','branch','group','companyname')
    users = [json.loads(user.to_json(follow_reference=True)) for user in users]
    for index, user in enumerate(users):
        if 'group' not in user:
            user['group'] = {"name": ""}
        if 'branch' not in user:
            user['branch'] = {"code": ""}
        user['role'] = list(roles.keys())[list(roles.values()).index(user['role'])].capitalize()
        user['status'] = list(userstatus.keys())[list(userstatus.values()).index(user['status'])].capitalize()
    return jsonify(data=users)

@general.route('/get-party-details/', methods=['GET', 'POST'])
@login_required
def getpartydetails():
    user = json.loads(User.objects(pk=request.form["id"]).first().to_json(follow_reference=True))

    data = {
        "id" : user['id'] if 'id' in user else "",
        "role" : user['role'] if 'role' in user else "",
        "branch" : user['branch']['id'] if 'branch' in user else "",
        "category" : user['category'] if 'category' in user else "",
        "group" : user['group']['id'] if 'group' in user else "",
        "companyname" : user['companyname'] if 'companyname' in user else "",
        "fullname" : user['fullname'] if 'fullname' in user else "",
        "email" : user['email'] if 'email' in user else "",
        "mobilenumber" : user['mobilenumber'] if 'mobilenumber' in user else "",
        "gstin" : user['gstin'] if 'gstin' in user else "",
        "billingaddress" : user['billingaddress'] if 'billingaddress' in user else "",
        "city" : user['city'] if 'city' in user else "",
        "state" : user['state'] if 'state' in user else "",
        "pincode" : user['pincode'] if 'pincode' in user else "",
        "openingbalance" : user['openingbalance'] if 'openingbalance' in user else "",
        "openingbalancedate" : datetime.fromtimestamp(float(user['openingbalancedate'])).strftime("%d/%m/%Y") if 'openingbalancedate' in user else "",
        "status" : user['status'] if 'status' in user else "",
        "whatsapp" : user['whatsapp'] if 'whatsapp' in user else False
    }

    brands_data = ["label_" + str(brand.name).replace(" ","_").strip() for brand in Brands.objects()]
    for key in brands_data:
        data[key] = json.loads(user["brand"])[key] if key in json.loads(user["brand"]) else "NA",

    return jsonify(data)