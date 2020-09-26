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
from werkzeug.utils import secure_filename


# Import app components
from app import db, jwt, bcrypt, login_manager, gst, app#, dropzone

# Import module forms
from app.dashboard.general.forms import BranchForm, PartyForm, ProductForm

# Importing Schema
from app.schema import Branches, User, roles, userstatus, User_Groups, Products, Brands, Product_Groups, Product_Sub_Groups, Taxes, Units, Products, Colours, ProductDesign

# Importing User UID generator
from app.auth.controller import getnextid

# Importing API's
from app.api.controller import sendSMS, checkSMSBalance

general = Blueprint('general', __name__, url_prefix='/dashboard')

def generate_password(length):
    return "".join(choice(string.ascii_uppercase + string.digits) for _ in range(length))

def get_new_barcode():
    while True:
        barcode = str(int(round(time.time() * 1000)))
        if not Products.objects(barcode=barcode):
            return barcode

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
                    userclass = form.userclass.data,
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
                    userclass = form.userclass.data,
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
    users = User.objects(role__lte=current_user.role, status__ne=userstatus['deleted'], pk__ne=current_user.pk).only('uid','fullname','mobilenumber','gstin','openingbalance','category','role','status','branch','group','companyname', 'userclass')
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
        "userclass" : user['userclass'],
        "openingbalancedate" : datetime.fromtimestamp(float(user['openingbalancedate'])).strftime("%d/%m/%Y") if 'openingbalancedate' in user else "",
        "status" : user['status'] if 'status' in user else "",
        "whatsapp" : user['whatsapp'] if 'whatsapp' in user else False
    }

    brands_data = ["label_" + str(brand.name).replace(" ","_").strip() for brand in Brands.objects()]
    for key in brands_data:
        data[key] = json.loads(user["brand"])[key] if key in json.loads(user["brand"]) else "NA",

    return jsonify(data)

@general.route('/products/', methods=['GET', 'POST'])
@login_required
def products():
    return render_template('dashboard/general/products.html')

@general.route('/get-all-products/', methods=['GET', 'POST'])
@login_required
def getallproducts():
    products = Products.objects().only('code','barcode','name','unitofmeasure','sellingprice','tax','discountprice','minstock')
    products = [json.loads(product.to_json(follow_reference=True)) for product in products]
    return jsonify(data=products)

@general.route('/new-product/', methods=['GET', 'POST'])
@login_required
def newproduct():
    form = ProductForm(request.form)

    if form.addDesign.data:
        form.designs.append_entry()

    if form.removeDesign.data:
        if len(form.designs) > 1:
            form.designs.pop_entry()

    if request.method == 'POST' and not form.removeDesign.data and not form.addDesign.data:
        designsList = []
        for design in form.designs:
            try:
                filename = str(form.barcode.data) + str(design.photo.name).split("-")[1] + "." + request.files[design.photo.name].filename.split(".")[-1]
                filepath = os.path.join(os.path.join(app.root_path, 'static/assets/images/products'), filename)
                image_data = request.files[design.photo.name].read()
                open(filepath, 'wb').write(image_data)
            except:
                filepath = "None"

            status = ProductDesign(
                code = str(form.barcode.data) + str(design.photo.name).split("-")[1],
                name = design.designname.data,
                colour = [Colours.objects(pk=col).first().to_dbref() for col in design.colour.data],
                photo = filepath
            ).save()
            if(status):
                designsList.append(status.to_dbref())

        product = Products(
            producttype = form.producttype.data,
            code = form.code.data,
            barcode = form.barcode.data,
            name = form.name.data,
            brand = Brands.objects(pk=form.brand.data).first().to_dbref() if form.brand.data else None,
            group = Product_Groups.objects(pk=form.group.data).first().to_dbref() if form.group.data else None,
            subgroup = Product_Sub_Groups.objects(pk=form.subgroup.data).first().to_dbref() if form.subgroup.data else None,
            tax = Taxes.objects(pk=form.tax.data).first().to_dbref() if form.tax.data else None,
            cess = Taxes.objects(pk=form.cess.data).first().to_dbref() if form.cess.data else None,
            unitofmeasure = Units.objects(pk=form.unitofmeasure.data).first().to_dbref() if form.unitofmeasure.data else None,
            length = float(form.length.data),
            width = float(form.width.data),
            unit = form.unit.data,
            sellingprice = float(form.sellingprice.data),
            minstock = int(form.minstock.data),
            costprice = float(form.costprice.data),
            discountprice = float(form.discountprice.data),
            sellingpricetype = form.sellingpricetype.data,
            costpricetype = form.costpricetype.data,
            discounttype = form.discounttype.data,
            productdesign = designsList,
            seller = current_user.pk,
            productclass = form.productclass.data,
            status = True
        ).save()

        if product:
            flash("New Product added Successfully", "success")
            return redirect(url_for('general.products'))

        flash("Failed to add Product","error")
        return redirect(url_for('general.products'))

    form.barcode.data = get_new_barcode()
    form.brand.choices = [(str(brand.pk),str(brand.name)) for brand in Brands.objects()]
    form.group.choices = [("","-- NA --")] + [(str(group.pk),str(group.name)) for group in Product_Groups.objects()]
    form.subgroup.choices = [("","-- NA --")] + [(str(subgroup.pk),str(subgroup.name)) for subgroup in Product_Sub_Groups.objects()]
    form.tax.choices = [(str(tax.pk),str(tax.name)) for tax in Taxes.objects(taxtype="IGST")]
    form.cess.choices = [("","-- NA --")] + [(str(tax.pk),str(tax.name)) for tax in Taxes.objects(taxtype="CESS")]
    form.unitofmeasure.choices = [(unit["id"],unit["name"]) for unit in Units.objects()]
    for design in form.designs:
        design.colour.choices = [(str(col.pk),str(col.name)) for col in Colours.objects()]

    return render_template('dashboard/general/new-product.html',form=form)

@general.route('/edit-product/', methods=['GET', 'POST'])
@login_required
def editproduct():
    form = ProductForm(request.form)

    product = Products.objects(barcode = request.args.get('barcode')).first()
    product = json.loads(product.to_json(follow_reference=True))

    if form.addDesign.data:
        form.designs.append_entry()

    if form.removeDesign.data:
        if len(form.designs) > 1:
            form.designs.pop_entry()
        if len(form.designs) < len(product["productdesign"]):
            product["productdesign"].pop()

    if request.method == 'POST' and not form.removeDesign.data and not form.addDesign.data:
        product = Products.objects(barcode = request.args.get('barcode')).first()
        product = json.loads(product.to_json(follow_reference=True))
        designsList = []
        newdesignIDS = [design.designid.data for design in form.designs]
        for index, productDesignData in enumerate(product["productdesign"]):
            if productDesignData['id'] not in newdesignIDS:
                ProductDesign.objects(pk=productDesignData['id']).first().delete()
                product["productdesign"].pop(index)

        designsList = [ProductDesign.objects(pk=productItem['id']).first().to_dbref() for productItem in product["productdesign"]]

        for design in form.designs:
            if (design.designid.data):
                # Existing Object
                if request.files[design.photo.name].filename:
                    filename = str(form.barcode.data) + str(design.photo.name).split("-")[1] + "." + request.files[design.photo.name].filename.split(".")[-1]
                    filepath = os.path.join(os.path.join(app.root_path, 'static/assets/images/products'), filename)
                    image_data = request.files[design.photo.name].read()
                    open(filepath, 'wb').write(image_data)

                    status = ProductDesign.objects(pk=design.designid.data).update(
                        code = str(form.barcode.data) + str(design.photo.name).split("-")[1],
                        name = design.designname.data,
                        colour = [Colours.objects(pk=col).first().to_dbref() for col in design.colour.data],
                        photo = filepath
                    )
                else:
                    status = ProductDesign.objects(pk=design.designid.data).update(
                        code = str(form.barcode.data) + str(design.photo.name).split("-")[1],
                        name = design.designname.data,
                        colour = [Colours.objects(pk=col).first().to_dbref() for col in design.colour.data]
                    )
            else:
                # New Object
                try:
                    filename = str(form.barcode.data) + str(design.photo.name).split("-")[1] + "." + request.files[design.photo.name].filename.split(".")[-1]
                    filepath = os.path.join(os.path.join(app.root_path, 'static/assets/images/products'), filename)
                    image_data = request.files[design.photo.name].read()
                    open(filepath, 'wb').write(image_data)
                except:
                    filepath = "None"

                status = ProductDesign(
                    code = str(form.barcode.data) + str(design.photo.name).split("-")[1],
                    name = design.designname.data,
                    colour = [Colours.objects(pk=col).first().to_dbref() for col in design.colour.data],
                    photo = filepath
                ).save()
                if(status):
                    designsList.append(status.to_dbref())

        product = Products.objects(barcode = form.barcode.data).first().update(
            producttype = form.producttype.data,
            code = form.code.data,
            barcode = form.barcode.data,
            name = form.name.data,
            brand = Brands.objects(pk=form.brand.data).first().to_dbref() if form.brand.data else None,
            group = Product_Groups.objects(pk=form.group.data).first().to_dbref() if form.group.data else None,
            subgroup = Product_Sub_Groups.objects(pk=form.subgroup.data).first().to_dbref() if form.subgroup.data else None,
            tax = Taxes.objects(pk=form.tax.data).first().to_dbref() if form.tax.data else None,
            cess = Taxes.objects(pk=form.cess.data).first().to_dbref() if form.cess.data else None,
            unitofmeasure = Units.objects(pk=form.unitofmeasure.data).first().to_dbref() if form.unitofmeasure.data else None,
            length = float(form.length.data),
            width = float(form.width.data),
            unit = form.unit.data,
            sellingprice = float(form.sellingprice.data),
            minstock = int(form.minstock.data),
            costprice = float(form.costprice.data),
            discountprice = float(form.discountprice.data),
            sellingpricetype = form.sellingpricetype.data,
            costpricetype = form.costpricetype.data,
            discounttype = form.discounttype.data,
            productdesign = designsList,
            productclass = form.productclass.data,
            status = True
        )

        if product:
            flash("New Product added Successfully", "success")
            return redirect(url_for('general.products'))

        flash("Failed to add Product","error")
        return redirect(url_for('general.products'))

    form.brand.choices = [(str(brand.pk),str(brand.name)) for brand in Brands.objects()]
    form.group.choices = [("","-- NA --")] + [(str(group.pk),str(group.name)) for group in Product_Groups.objects()]
    form.subgroup.choices = [("","-- NA --")] + [(str(subgroup.pk),str(subgroup.name)) for subgroup in Product_Sub_Groups.objects()]
    form.tax.choices = [(str(tax.pk),str(tax.name)) for tax in Taxes.objects(taxtype="IGST")]
    form.cess.choices = [("","-- NA --")] + [(str(tax.pk),str(tax.name)) for tax in Taxes.objects(taxtype="CESS")]
    form.unitofmeasure.choices = [(unit["id"],unit["name"]) for unit in Units.objects()]

    if not form.is_submitted():
        for _ in range(len(product["productdesign"]) - 1):
            form.designs.append_entry()

    for design in form.designs:
        design.colour.choices = [(str(col.pk),str(col.name)) for col in Colours.objects()]

    if not form.is_submitted():
        form.producttype.data = product["producttype"]
        form.code.data = product["code"]
        form.barcode.data = product["barcode"]
        form.name.data = product["name"]
        form.brand.data = product["brand"]["id"] if "brand" in product else ""
        form.group.data = product["group"]["id"] if "group" in product else ""
        form.subgroup.data = product["subgroup"]["id"] if "subgroup" in product else ""
        form.tax.data = product["tax"]["id"] if "tax" in product else ""
        form.cess.data = product["cess"]["id"] if "cess" in product else ""
        form.unitofmeasure.data = product["unitofmeasure"]["id"] if "unitofmeasure" in product else ""
        form.length.data = product["length"]
        form.width.data = product["width"]
        form.unit.data = product["unit"]
        form.sellingprice.data = product["sellingprice"]
        form.minstock.data = product["minstock"]
        form.costprice.data = product["costprice"]
        form.discountprice.data = product["discountprice"]
        form.sellingpricetype.data = product["sellingpricetype"]
        form.costpricetype.data = product["costpricetype"]
        form.discounttype.data = product["discounttype"]
        form.productclass.data = product["productclass"]
        
        for index, productDesignData in enumerate(product["productdesign"]):
            form.designs[index].designid.data = productDesignData['id']
            form.designs[index].designname.data = productDesignData['name']
            data = []
            for color in productDesignData['colour']:
                data.append(color['id'])
            form.designs[index].colour.data = data

    return render_template('dashboard/general/edit-product.html',form=form)