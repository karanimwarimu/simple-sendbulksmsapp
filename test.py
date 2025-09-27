from flask import Flask
import requests

app = Flask(__name__)

# API Config
API_URL = "https://quicksms.advantasms.com/api/services/sendbulk/"
PARTNER_ID = "11945"
API_KEY = "e00720e5316dafe1ed04c3fc2fe6cf4e"
SHORTCODE = "AdvantaSMS"

# Define recipients (id, name, number)
recipients = [
    {"id": 1, "name": "Karani", "mobile": "254759711993"},
    {"id": 2, "name": "Baraka", "mobile": "0714590103"}
]


@app.route("/send-test-sms")
def send_sms():
    sms_list = []
    for r in recipients:
        sms_list.append({
            "partnerID": PARTNER_ID,
            "apikey": API_KEY,
            "pass_type": "plain",
            "clientsmsid": r["id"],
            "mobile": r["mobile"],
            "message": f"Hi {r['name']}, test message :) ",
            "shortcode": SHORTCODE
        })

    payload = {
        "count": len(sms_list),
        "smslist": sms_list
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)

    return f"Response from SMS API: {response.text}"

if __name__ == "__main__":
    with app.app_context():
        print(send_sms())  
    app.run(debug=True)
