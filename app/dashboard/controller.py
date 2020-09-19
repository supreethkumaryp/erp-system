from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import login_required, logout_user, current_user, logout_user

# Import app components
from app import db, jwt, bcrypt, login_manager

# Import module forms
from app.dashboard.forms import EditUserInfoForm, EditUserPasswordForm

# Importing Schema
from app.schema import User, userstatus

# Defining the blueprint: 'dashboard', set its url prefix: app.url/dashboard
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template("dashboard/dashboard.html")

# @dashboard.route('/edit-profile/', methods=['GET', 'POST'])
# @login_required
# def editprofile():
#     userinfoform = EditUserInfoForm(request.form)
#     userpasswordform = EditUserPasswordForm(request.form)
    
#     if request.method == 'GET':
#         for key in userinfoform:
#             if key.id not in ["samebilladdress", "csrf_token", "whatsapp", "submituserinfo"]:
#                 exec("userinfoform.%s.data = current_user.%s" % (key.id, key.id))
#         userinfoform.samebilladdress.data = True if current_user.communicationaddress == current_user.billingaddress else False
#         userinfoform.whatsapp.data = True if current_user.whatsapp else False

#     if request.method == 'POST' and userinfoform.submituserinfo.data and userinfoform.validate():
#         if userinfoform.gstin.data != "":
#             # Validate GST Number Pattern.
#             if (not gst.checkpattern(userinfoform.gstin.data)):
#                 flash("Invalid GST Pattern!", "error")
#                 return redirect(url_for('general.parties'))

#             # Validate GST Number Checksum.
#             if (not gst.checkchecksum(userinfoform.gstin.data)):
#                 flash("Invalid GST Number!", "error")
#                 return redirect(url_for('general.parties'))

#         user = User.objects(uid=userinfoform.uid.data).update(
#             category = userinfoform.category.data,
#             companyname = userinfoform.companyname.data if userinfoform.category.data == "company" else "",
#             fullname = userinfoform.fullname.data,
#             email = userinfoform.email.data if userinfoform.email.data else None,
#             mobilenumber = userinfoform.mobilenumber.data,
#             whatsapp = userinfoform.whatsapp.data,
#             gstin = userinfoform.gstin.data,
#             communicationaddress = userinfoform.communicationaddress.data,
#             billingaddress = userinfoform.billingaddress.data,
#             state = userinfoform.state.data,
#             city = userinfoform.city.data,
#             pincode = userinfoform.pincode.data,
#             brand = userinfoform.brand.data
#         )
#         if user:
#             flash("Profile Updated Successfully", "success")
#             return redirect(url_for('dashboard.editprofile'))   

#         flash("Failed to Profile", "error")
#         return redirect(url_for('dashboard.editprofile'))

#     if request.method == 'POST' and userpasswordform.submituserpassword.data and userpasswordform.validate():
#         if bcrypt.check_password_hash(current_user.password, userpasswordform.oldpassword.data):

#             if userpasswordform.newpassword.data != userpasswordform.retypenewpassword.data:
#                 flash("Password and Confirm Password did't Match", "error")
#                 return redirect(url_for('dashboard.editprofile'))

#             user = User(pk=current_user.pk).update(
#                 password = bcrypt.generate_password_hash(userpasswordform.newpassword.data).decode("utf-8")
#             )

#             if user:
#                 flash("Password Updated Successfully", "success")
#                 return redirect(url_for('auth.logout'))

#             flash("Failed to Update Password", "error")
#             return redirect(url_for('dashboard.editprofile'))

#         flash("Incorrect Old Password", "error")
#         return redirect(url_for('dashboard.editprofile'))

#     return render_template('dashboard/edit-profile.html', userinfoform=userinfoform, userpasswordform=userpasswordform)