import os
import threading
from flask import Flask
import discord
from discord.ext import commands

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Discord UI Button View
class ApproveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent button

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_button")
    async def approve_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Approved successfully!", ephemeral=True)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Your target Discord Channel ID
CHANNEL_ID = 1558729581244977185 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Click below to approve:", view=ApproveView())
    else:
        print(f"Could not find channel with ID {CHANNEL_ID}")

bot.run(os.environ.get("DISCORD_TOKEN"))