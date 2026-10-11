import os
from flask import Flask
import threading

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render assigns a PORT dynamically via environment variables
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Run Flask server in a separate thread to keep Render alive
threading.Thread(target=run_flask, daemon=True).start()

# Discord Bot Setup
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Fetch the bot token safely from environment variables
bot.run(os.environ.get("DISCORD_TOKEN"))