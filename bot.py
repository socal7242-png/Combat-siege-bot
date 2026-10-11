import os
import threading
import asyncio
from flask import Flask, request
import discord
from discord.ext import commands
from discord.ui import Button, View

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

# Interactive View with "Approve User" Button
class ApproveView(View):
    def __init__(self, game_name, game_password):
        super().__init__(timeout=None)  # Keeps button active indefinitely
        self.game_name = game_name
        self.game_password = game_password

    @discord.ui.button(label="Approve User", style=discord.ButtonStyle.success, emoji="✅")
    async def approve_button_callback(self, interaction: discord.Interaction, button: Button):
        # Disable button after click so it can't be spammed
        button.disabled = True
        button.label = "Approved"
        await interaction.response.edit_message(view=self)
        
        # Send confirmation note in channel
        await interaction.followup.send(
            f"🎉 **User Approved!**\n"
            f"**Game Name:** `{self.game_name}`\n"
            f"**Game Password:** `{self.game_password}`\n"
            f"*(Remember to update your `approved_users.json` Gist with these credentials!)*"
        )

async def send_credential_alert(game_name, game_password):
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            view = ApproveView(game_name, game_password)
            await channel.send(
                f"🆕 **NEW SIGN UP REQUEST!**\n"
                f"🎮 **Game Name:** `{game_name}`\n"
                f"🔑 **Game Password:** `{game_password}`",
                view=view
            )
            print("SUCCESS: Credentials and Approve button posted to Discord!")
        else:
            print(f"ERROR: Could not find channel {CHANNEL_ID}.")
    except Exception as e:
        print(f"ERROR: Failed to send message to Discord: {e}")

@app.route('/submit', methods=['POST'])
def handle_submission():
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