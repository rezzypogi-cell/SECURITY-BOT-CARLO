import subprocess
import sys

# --- AUTO-INSTALL DEPENDENCIES (SINGLE-FILE DEPLOYMENT) ---
required_packages = ["discord.py", "aiohttp"]
for package in required_packages:
    try:
        __import__(package.replace(".py", ""))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import discord
from discord import app_commands
from discord.ext import commands
import re
import time
import asyncio
from datetime import timedelta, datetime, timezone
from collections import defaultdict
import traceback
import aiohttp
import os

# --- LOAD TOKEN AND WEBHOOK FROM Token.txt ---
TOKEN = ""
WEBHOOK_URL = ""

if os.path.exists("Token.txt"):
    with open("Token.txt", "r") as f:
        lines = f.read().splitlines()
        if len(lines) > 0:
            TOKEN = lines[0].strip()
        if len(lines) > 1:
            WEBHOOK_URL = lines[1].strip()
else:
    print("[ERROR] Token.txt file not found! Please create Token.txt containing your bot token and webhook URL.")

# Security Threshold Constants
RAID_JOIN_LIMIT = 5
RAID_TIME_WINDOW = 10
MAX_MENTIONS_ALLOWED = 3
SPAM_MESSAGE_LIMIT = 4
SPAM_TIME_WINDOW = 4
BOT_SPAM_LIMIT = 3
BOT_SPAM_WINDOW = 3
MIN_ACCOUNT_AGE_DAYS = 3
MAX_ATTACHMENTS_ALLOWED = 2

# Discord Intents Setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.webhooks = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

# Trackers and Dictionaries
join_tracker = []
user_message_tracker = defaultdict(list)
bot_message_tracker = defaultdict(list)
last_message_content = defaultdict(str)
security_channels = {}

# Security Modules Status Dictionary
security_modules = {
    "antibot": True,
    "antinuke": True,
    "antilink": True,
    "antimassmention": True,
    "antispam": True,
    "antiraid": True,
    "antialt": True,
    "antiattachment": True,
    "antiwebhook": True,
    "antirole": True
}

# Strict URL & Invite Link Detection Pattern
STRICT_URL_PATTERN = re.compile(
    r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|edu|gov|mil|io|gg|me|co|xyz|tk|ml|ga|cf|gq|ru|su|to|is|cc|ws|to|tv|fm|am|nu|la|ms|sh|st|in|pk|bd|cn|jp|kr|br|mx|ar|cl|co|ve|pe|uy|py|bo|ec|gt|hn|sv|ni|cr|pa|cu|do|ht|jm|bb|bs|gy|sr|fk|vg|vi|tc|ky|bm|ai|ag|dm|gd|kn|lc|vc|tt|pr)[^\s]*|discord\.(gg|com/invite|me|io|plus|link|net)/[^\s]+)',
    re.IGNORECASE
)

BLACK_COLOR = discord.Color.from_rgb(20, 20, 20)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"[ONLINE] Public Security Bot logged in as {bot.user.name}")
        print(f"[STATUS] Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.event
async def on_guild_join(guild: discord.Guild):
    if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        return

    installer_name = "Unknown / Direct Link"
    installer_id = "N/A"
    installer_avatar = None

    try:
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.bot_add):
            if entry.target and entry.target.id == bot.user.id:
                if entry.user:
                    installer_name = str(entry.user)
                    installer_id = str(entry.user.id)
                    installer_avatar = entry.user.display_avatar.url
                break
    except Exception as e:
        print(f"Error fetching installer audit log: {e}")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
        
        embed = discord.Embed(
            title="BOT ADDED TO A NEW SERVER",
            color=BLACK_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Server Name", value=f"`{guild.name}`", inline=True)
        embed.add_field(name="Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Member Count", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Server Owner", value=f"<@{guild.owner_id}> (`{guild.owner_id}`)", inline=False)
        embed.add_field(name="Added By (Installer)", value=f"`{installer_name}` (`{installer_id}`)", inline=False)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        if installer_avatar:
            embed.set_footer(text=f"Installer ID: {installer_id}", icon_url=installer_avatar)
        else:
            embed.set_footer(text=f"Bot Security System | Server ID: {guild.id}")

        try:
            await webhook.send(embed=embed, username="Bot Tracking System")
        except Exception as e:
            print(f"Failed to send webhook notification: {e}")

if __name__ == "__main__":
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"--- BOT ERROR ENCOUNTERED ---\n{e}")
    else:
        print("[CRITICAL ERROR] Bot token is missing or Token.txt is empty!")