from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import login_required, logout_user, current_user, logout_user
from wtforms import StringField
import json

# Import app components
from app import db, jwt, bcrypt, login_manager

# Import module forms
from app.dashboard.forms import EditUserInfoForm, EditUserPasswordForm

# Importing Schema
from app.schema import User, userstatus, Brands, Wallet

# Defining the blueprint: 'dashboard', set its url prefix: app.url/dashboard
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.role >= 32:
        smsBalance = Wallet.objects(name="sms").first().balance
        whatsappBalance = Wallet.objects(name="whatsapp").first().balance
        return render_template("dashboard/dashboard-admin.html", smsBalance=smsBalance, whatsappBalance=whatsappBalance)
    else:
        print("Test")
        return render_template('error/coming-soon.html')

@dashboard.route('/edit-profile/', methods=['GET', 'POST'])
@login_required
def editprofile():

    brands_data = ["label_" + str(brand.name).replace(" ","_").strip() for brand in Brands.objects()]
    labelsFields = []
    for key in brands_data:
        setattr(EditUserInfoForm, key, StringField(" ".join(str(key).split("_")[1:]) + " Label", id=key, _name=key))

    userinfoform = EditUserInfoForm(request.form)
    userpasswordform = EditUserPasswordForm(request.form)
    if request.method == 'GET':
        for key in userinfoform:
            if str(key.id).startswith("label_"):
                exec("userinfoform.%s.data = json.loads(current_user.brand)['%s'] if '%s' in json.loads(current_user.brand).keys() else 'NA'" % (key.id, key.id, key.id))
                labelsFields.append(key)
            elif key.id not in ["samebilladdress", "csrf_token", "whatsapp", "submituserinfo"]:
                exec("userinfoform.%s.data = current_user.%s" % (key.id, key.id))
        userinfoform.samebilladdress.data = True if current_user.communicationaddress == current_user.billingaddress else False
        userinfoform.whatsapp.data = True if current_user.whatsapp else False

    if request.method == 'POST' and userinfoform.submituserinfo.data and userinfoform.validate():
        if userinfoform.gstin.data != "":
            # Validate GST Number Pattern.
            if (not gst.checkpattern(userinfoform.gstin.data)):
                flash("Invalid GST Pattern!", "error")
                return redirect(url_for('general.parties'))

            # Validate GST Number Checksum.
            if (not gst.checkchecksum(userinfoform.gstin.data)):
                flash("Invalid GST Number!", "error")
                return redirect(url_for('general.parties'))

        temp_labels = {}
        for key in userinfoform.data.items():
            if key[0].startswith('label_'):
                temp_labels[key[0]] = key[1] if key[1] else "NA"

        user = User.objects(uid=userinfoform.uid.data).update(
            category = userinfoform.category.data,
            companyname = userinfoform.companyname.data if userinfoform.category.data == "company" else "",
            fullname = userinfoform.fullname.data,
            email = userinfoform.email.data if userinfoform.email.data else None,
            mobilenumber = userinfoform.mobilenumber.data,
            whatsapp = userinfoform.whatsapp.data,
            gstin = userinfoform.gstin.data,
            communicationaddress = userinfoform.communicationaddress.data,
            billingaddress = userinfoform.billingaddress.data,
            state = userinfoform.state.data,
            city = userinfoform.city.data,
            pincode = userinfoform.pincode.data,
            brand = json.dumps(temp_labels)
        )
        if user:
            flash("Profile Updated Successfully", "success")
            return redirect(url_for('dashboard.editprofile'))   

        flash("Failed to Profile", "error")
        return redirect(url_for('dashboard.editprofile'))

    if request.method == 'POST' and userpasswordform.submituserpassword.data and userpasswordform.validate():
        if bcrypt.check_password_hash(current_user.password, userpasswordform.oldpassword.data):

            if userpasswordform.newpassword.data != userpasswordform.retypenewpassword.data:
                flash("Password and Confirm Password did't Match", "error")
                return redirect(url_for('dashboard.editprofile'))

            user = User(pk=current_user.pk).update(
                password = bcrypt.generate_password_hash(userpasswordform.newpassword.data).decode("utf-8")
            )

            if user:
                flash("Password Updated Successfully", "success")
                return redirect(url_for('auth.logout'))

            flash("Failed to Update Password", "error")
            return redirect(url_for('dashboard.editprofile'))

        flash("Incorrect Old Password", "error")
        return redirect(url_for('dashboard.editprofile'))

    return render_template('dashboard/edit-profile.html', userinfoform=userinfoform, userpasswordform=userpasswordform, brands_data=labelsFields)