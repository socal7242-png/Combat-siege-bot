import os
import threading
import asyncio
import json
import requests
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
GIST_ID = os.environ.get("GIST_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def update_github_gist(game_name, game_password):
    """Fetches current approved_users.json from Gist, appends new user, and updates Gist."""
    if not GIST_ID or not GITHUB_TOKEN:
        print("ERROR: Missing GIST_ID or GITHUB_TOKEN in environment variables!")
        return False, "Missing GitHub credentials in Render environment."

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    gist_url = f"https://api.github.com/gists/{GIST_ID}"
    
    try:
        # Step 1: Fetch existing Gist data
        res = requests.get(gist_url, headers=headers)
        if res.status_code != 200:
            return False, f"Failed to fetch Gist (HTTP {res.status_code})"
        
        gist_data = res.json()
        filename = "approved_users.json"
        
        if filename not in gist_data["files"]:
            filename = list(gist_data["files"].keys())[0]

        current_content_str = gist_data["files"][filename]["content"]
        
        # Parse existing JSON content
        try:
            users_dict = json.loads(current_content_str)
        except Exception:
            users_dict = {}

        # Step 2: Add new credentials
        users_dict[game_name] = game_password

        # Step 3: Send PATCH request to update Gist
        updated_content_str = json.dumps(users_dict, indent=4)
        patch_payload = {
            "files": {
                filename: {
                    "content": updated_content_str
                }
            }
        }
        
        patch_res = requests.patch(gist_url, headers=headers, json=patch_payload)
        if patch_res.status_code == 200:
            return True, "User successfully added to Gist!"
        else:
            return False, f"Failed to update Gist (HTTP {patch_res.status_code})"

    except Exception as e:
        return False, str(e)


# Interactive View with Automatic Approval
class ApproveView(View):
    def __init__(self, game_name, game_password):
        super().__init__(timeout=None)
        self.game_name = game_name
        self.game_password = game_password

    @discord.ui.button(label="Approve User", style=discord.ButtonStyle.success, emoji="✅")
    async def approve_button_callback(self, interaction: discord.Interaction, button: Button):
        button.disabled = True
        button.label = "Processing..."
        await interaction.response.edit_message(view=self)
        
        # Perform automatic Gist update
        success, message = update_github_gist(self.game_name, self.game_password)
        
        if success:
            button.label = "Approved & Added"
            await interaction.edit_original_response(view=self)
            await interaction.followup.send(
                f"✅ **AUTOMATIC APPROVAL COMPLETE!**\n"
                f"🎮 **Game Name:** `{self.game_name}`\n"
                f"🔑 **Game Password:** `{self.game_password}`\n"
                f"🚀 *Added directly to `approved_users.json`! The user can now log in immediately.*"
            )
        else:
            button.disabled = False
            button.label = "Approve User"
            await interaction.edit_original_response(view=self)
            await interaction.followup.send(
                f"❌ **APPROVAL FAILED!**\n"
                f"Error: `{message}`"
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