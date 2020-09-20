from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
import requests, json

# Importing schema
from app.schema import Wallet

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

@api.route('/get-text-sms-balance/', methods=['GET', 'POST'])
def gettextsmsbalance():
    url = "https://www.fast2sms.com/dev/wallet"
    headers = {
        'authorization': "ZmICZWh5fTvbFW4TsZA0phUKEgeuXoGSbkawga2ipKziKAO8nl4SrGKeOqdj",
        }
    response = requests.request("POST", url, headers=headers)

    return jsonify(
        walletBalance = json.loads(response.text)["wallet"],
        smsBalance = str(int(float(json.loads(response.text)["wallet"]) / 0.90)),
        originalSMSBalance = str(int(float(json.loads(response.text)["wallet"]) / 0.20))
    )

# Function to check Balance
def checkSMSBalance(mode="sms"):
    if mode=="sms" or mode=="whatsapp":
        return int(Wallet.objects(name=mode).first().balance)
    else:
        return False

# Function to send SMS
def sendSMS(mobileNumber, MSG, mode="sms"):
    balance = checkSMSBalance(mode)
    if not balance:
        return False

    mobileNumber = str(mobileNumber).replace("+91","").replace("-","").replace(" ","").strip()
    if mode=="sms":
        url = "https://www.fast2sms.com/dev/bulk"
        querystring = {
            "authorization": "ZmICZWh5fTvbFW4TsZA0phUKEgeuXoGSbkawga2ipKziKAO8nl4SrGKeOqdj",
            "sender_id": "FSTSMS",
            "message": MSG,
            "language": "english",
            "route":"p",
            "numbers": mobileNumber
        }
        headers = {
            'cache-control': "no-cache"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        wallet = Wallet.objects(name="sms").first()
        wallet.balance = balance - 1
        wallet.save()

        return bool(json.loads(response.text)["return"])

    elif mode=="whatsapp":
        pass
    else:
        return False
