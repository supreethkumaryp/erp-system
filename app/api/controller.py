from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
import requests

# Defining the blueprint: 'auth', set its url prefix: app.url/auth
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/get-pincode-details/', methods=['GET', 'POST'])
def getpincodedetails():
    pincodedata = requests.get("http://www.postalpincode.in/api/pincode/"+request.form["pincode"].strip()).json()
    # import json
    # print(json.dumps(pincodedata.json(),indent=4))
    if (pincodedata["Status"] == "Success"):
        city = pincodedata["PostOffice"][0]["District"].strip()
        state = pincodedata["PostOffice"][0]["State"].strip()
        
        return jsonify(status="success", city=city, state=state)

    return jsonify(status="error")