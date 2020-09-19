import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_login import login_required, current_user

# Import app components
from app import db, jwt, bcrypt, login_manager, gst

# Import module forms
from app.dashboard.masters.forms import TaxForm, UnitForm, BrandsForm, ProductGroupForm, ProductSubGroupForm, ManufacturingProcessForm, UserGroupsForm, Colour1Form

# Importing Schema
from app.schema import Taxes, Tax_Types, Units, Brands, Product_Groups, Product_Sub_Groups, Manufacturing_Process, User_Groups, Branches, Colours

masters = Blueprint('masters', __name__, url_prefix='/dashboard')

@masters.route('/taxes/', methods=['GET', 'POST'])
@login_required
def taxes():
    form = TaxForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        
        if not Taxes.objects(name=form.taxtype.data + " @ " + form.name.data):
            Taxes(
                taxtype = form.taxtype.data,
                name = form.taxtype.data + " @ " + form.name.data,
                percentage = float(form.percentage.data)
            ).save()

            flash("New Tax Added Successfully", "success")
            return redirect(url_for('masters.taxes'))
        
        else:
            flash("Tax Already Exist", "error")

    return render_template('dashboard/masters/taxes.html', form= form)

@masters.route('/get-all-taxes/', methods=['GET', 'POST'])
@login_required
def getalltaxes():
    taxes = json.loads(Taxes.objects().to_json())
    return jsonify(data=taxes)

@masters.route('/units/', methods=['GET', 'POST'])
@login_required
def units():
    form = UnitForm(request.form)
    form.baseunit.choices = [("", "Select Base Unit")] + [(str(unit.pk), unit.name) for unit in Units.objects()]
    
    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            if form.complexflag.data:
                Units(
                    code = form.code.data,
                    name = form.name.data,
                    complexflag = form.complexflag.data,
                    factor = float(form.factor.data),
                    baseunit = Units.objects(pk=form.baseunit.data).first().to_dbref()
                ).save()
            else:
                Units(
                    code = form.code.data,
                    name = form.name.data,
                    complexflag = form.complexflag.data
                ).save()

            flash("New Unit Added Successfully", "success")
            return redirect(url_for('masters.units'))

        else:
            if form.complexflag.data:
                Units(pk=form.id.data).update(
                    code = form.code.data,
                    name = form.name.data,
                    complexflag = form.complexflag.data,
                    factor = float(form.factor.data),
                    baseunit = Units.objects(pk=form.baseunit.data).first().to_dbref()
                )
            else:
                Units(pk=form.id.data).update(
                    code = form.code.data,
                    name = form.name.data,
                    complexflag = form.complexflag.data,
                    unset__factor = 1,
                    unset__baseunit = 1
                )
            
            flash("Updated Unit", "success")
            return redirect(url_for('masters.units'))

    return render_template('dashboard/masters/units.html', form=form)

@masters.route('/get-all-units/', methods=['GET', 'POST'])
@login_required
def getallunits():
    units = [json.loads(unit.to_json(follow_reference=True)) for unit in Units.objects()]
    return jsonify(data=units)

@masters.route('/get-unit-details/', methods=['GET', 'POST'])
@login_required
def getunit():
    unit = json.loads(Units.objects(pk=request.form["id"]).first().to_json(follow_reference=True))
    return jsonify(
        id = unit['id'],
        code = unit['code'],
        name = unit['name'],
        complexflag = unit['complexflag'],
        factor = unit['factor'] if "factor" in unit else 0,
        baseunit = unit['baseunit']['id'] if "baseunit" in unit else ""
    )

# @masters.route('/delete-unit/', methods=['GET', 'POST'])
# @login_required
# def deleteunit():
#     status = Units.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/brands/', methods=['GET', 'POST'])
@login_required
def brands():
    form = BrandsForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            Brands(
                code = form.code.data,
                name = form.name.data
            ).save()

            flash("New Brand Added Successfully", "success")
            return redirect(url_for('masters.brands'))

        else:
            Brands(pk=form.id.data).update(
                code = form.code.data,
                name = form.name.data
            )
            
            flash("Updated Brand Successfully", "success")
            return redirect(url_for('masters.brands'))

    return render_template('dashboard/masters/brands.html', form=form)

@masters.route('/get-all-brands/', methods=['GET', 'POST'])
@login_required
def getallbrands():
    return jsonify(data=Brands.objects())

@masters.route('/get-brand-details/', methods=['GET', 'POST'])
@login_required
def getbrand():
    brand = Brands.objects(pk=request.form["id"]).first()
    return jsonify(
        id = str(brand.pk),
        code = brand.code,
        name = brand.name
    )

# @masters.route('/delete-brand/', methods=['GET', 'POST'])
# @login_required
# def deletebrand():
#     status = Brands.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/product-groups/', methods=['GET', 'POST'])
@login_required
def productgroups():
    form = ProductGroupForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            Product_Groups(
                code = form.code.data,
                name = form.name.data
            ).save()

            flash("New Product Group Successfully", "success")
            return redirect(url_for('masters.productgroups'))

        else:
            Product_Groups(pk=form.id.data).update(
                code = form.code.data,
                name = form.name.data
            )
            
            flash("Updated Product Group Successfully", "success")
            return redirect(url_for('masters.productgroups'))

    return render_template('dashboard/masters/productgroups.html', form=form)

@masters.route('/get-all-product-groups/', methods=['GET', 'POST'])
@login_required
def getallproductgroups():
    return jsonify(data=Product_Groups.objects())

@masters.route('/get-product-group-details/', methods=['GET', 'POST'])
@login_required
def getproductgroup():
    productgroup = Product_Groups.objects(pk=request.form["id"]).first()
    return jsonify(
        id = str(productgroup.pk),
        code = productgroup.code,
        name = productgroup.name
    )

# @masters.route('/delete-product-group/', methods=['GET', 'POST'])
# @login_required
# def deleteproductgroup():
#     status = Product_Groups.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/product-sub-groups/', methods=['GET', 'POST'])
@login_required
def productsubgroups():
    form = ProductSubGroupForm(request.form)
    form.productgroup.choices = [("", "Select Product Subgroup")] + [(str(productgroup.pk), productgroup.name) for productgroup in Product_Groups.objects()]
    
    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            Product_Sub_Groups(
                code = form.code.data,
                name = form.name.data,
                productgroup = Product_Groups.objects(pk=form.productgroup.data).first().to_dbref()
            ).save()

            flash("New Product Group Successfully", "success")
            return redirect(url_for('masters.productsubgroups'))

        else:
            Product_Sub_Groups(pk=form.id.data).update(
                code = form.code.data,
                name = form.name.data,
                productgroup = Product_Groups.objects(pk=form.productgroup.data).first().to_dbref()
            )
            
            flash("Updated Product Group Successfully", "success")
            return redirect(url_for('masters.productsubgroups'))

    return render_template('dashboard/masters/productsubgroups.html', form=form)

@masters.route('/get-all-product-sub-groups/', methods=['GET', 'POST'])
@login_required
def getallproductsubgroups():
    subgroup = [json.loads(subgroup.to_json(follow_reference=True)) for subgroup in Product_Sub_Groups.objects()]
    return jsonify(data=subgroup)

@masters.route('/get-product-sub-group-details/', methods=['GET', 'POST'])
@login_required
def getproductsubgroup():
    subgroup = json.loads(Product_Sub_Groups.objects(pk=request.form["id"]).first().to_json(follow_reference=True))
    return jsonify(
        id = subgroup['id'],
        code = subgroup['code'],
        name = subgroup['name'],
        productgroup = subgroup['productgroup']['id']
    )

# @masters.route('/delete-product-sub-group/', methods=['GET', 'POST'])
# @login_required
# def deleteproductsubgroup():
#     status = Product_Sub_Groups.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/manufacturing-process/', methods=['GET', 'POST'])
@login_required
def manufacturingprocess():
    form = ManufacturingProcessForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            Manufacturing_Process(
                code = form.code.data,
                name = form.name.data
            ).save()

            flash("New Manufacturing Process Added Successfully", "success")
            return redirect(url_for('masters.manufacturingprocess'))

        else:
            Manufacturing_Process(pk=form.id.data).update(
                code = form.code.data,
                name = form.name.data
            )
            
            flash("Updated Manufacturing Process Successfully", "success")
            return redirect(url_for('masters.manufacturingprocess'))

    return render_template('dashboard/masters/manufacturingprocess.html', form=form)

@masters.route('/get-all-manufacturing-process/', methods=['GET', 'POST'])
@login_required
def getallmanufacturingprocess():
    return jsonify(data=Manufacturing_Process.objects())

@masters.route('/get-manufacturing-process-details/', methods=['GET', 'POST'])
@login_required
def getmanufacturingprocess():
    manufacturingprocess = Manufacturing_Process.objects(pk=request.form["id"]).first()
    return jsonify(
        id = str(manufacturingprocess.pk),
        code = manufacturingprocess.code,
        name = manufacturingprocess.name
    )

# @masters.route('/delete-manufacturing-process/', methods=['GET', 'POST'])
# @login_required
# def deletemanufacturingprocess():
#     status = Manufacturing_Process.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/user-groups/', methods=['GET', 'POST'])
@login_required
def usergroups():
    form = UserGroupsForm(request.form)
    form.branch.choices = [("", "Select Branch")] + [(str(branch.pk), branch.name) for branch in Branches.objects()]
    
    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            User_Groups(
                name = form.name.data,
                branch = Branches.objects(pk=form.branch.data).first().to_dbref()
            ).save()

            flash("New User Group Successfully", "success")
            return redirect(url_for('masters.usergroups'))

        else:
            User_Groups(pk=form.id.data).update(
                name = form.name.data,
                branch = Branches.objects(pk=form.branch.data).first().to_dbref()
            )
            
            flash("Updated User Group Successfully", "success")
            return redirect(url_for('masters.usergroups'))

    return render_template('dashboard/masters/usergroups.html', form=form)

@masters.route('/get-all-user-groups/', methods=['GET', 'POST'])
@login_required
def getallusergroups():
    usergroups = [json.loads(usergroup.to_json(follow_reference=True)) for usergroup in User_Groups.objects()]
    return jsonify(data=usergroups)

@masters.route('/get-user-group-details/', methods=['GET', 'POST'])
@login_required
def getusergroup():
    usergroup = json.loads(User_Groups.objects(pk=request.form["id"]).first().to_json(follow_reference=True))
    return jsonify(
        id = usergroup['id'],
        name = usergroup['name'],
        branch = usergroup['branch']['id']
    )

# @masters.route('/delete-user-groups/', methods=['GET', 'POST'])
# @login_required
# def deleteusergroup():
#     status = User_Groups.objects(pk=request.form["id"]).first().delete()
#     return jsonify(status = True) if status else jsonify(status = False)

@masters.route('/colours/', methods=['GET', 'POST'])
@login_required
def colours_route():
    form = Colour1Form(request.form)
    
    if request.method == 'POST' and form.validate_on_submit():
        
        if form.id.data == "new":
            print(form.code.data)
            Colours(
                name = form.name.data,
                code = str(form.code.data)
            ).save()

            flash("New Colour Successfully", "success")
            return redirect(url_for('masters.colours_route'))

        else:
            Colours(pk=form.id.data).update(
                name = form.name.data,
                code = str(form.code.data)
            )
            
            flash("Updated User Group Successfully", "success")
            return redirect(url_for('masters.colours_route'))

    return render_template('dashboard/masters/colours.html', form=form)

@masters.route('/get-all-colours/', methods=['GET', 'POST'])
@login_required
def getallcolours():
    colours = [json.loads(colour.to_json(follow_reference=True)) for colour in Colours.objects()]
    return jsonify(data=colours)

@masters.route('/get-colour-details/', methods=['GET', 'POST'])
@login_required
def getcolour():
    colour = json.loads(Colours.objects(pk=request.form["id"]).first().to_json(follow_reference=True))
    return jsonify(
        id = colour['id'],
        name = colour['name'],
        code = colour['code']
    )