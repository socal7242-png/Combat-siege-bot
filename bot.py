import os
import json
import threading
import discord
import requests
from flask import Flask, request
from discord.ui import Button, View

# Your tokens and IDs
TOKEN = "MTU1ODc5NzQzOTE2NTUzODM2NA.GODATX.MW-xUKVJ9_ry5zNnEUvD4ie6gMoK-s8S-c2dkA"
CHANNEL_ID = int("1558729581244977185")
GITHUB_TOKEN = "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"
GIST_ID = "861d9ecfb5c88548669c8e3c92ea9bbb"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

app = Flask(__name__)

class ApprovalView(View):
    def __init__(self, username, password):
        super().__init__(timeout=None)
        self.username = username
        self.password = password

    @discord.ui.button(label="Approve User", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve_callback(self, interaction: discord.Interaction, button: Button):
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        url = f"https://api.github.com/gists/{GIST_ID}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            await interaction.response.send_message("❌ Failed to fetch Gist from GitHub.", ephemeral=True)
            return

        gist_data = response.json()
        filename = list(gist_data['files'].keys())[0]
        content = gist_data['files'][filename]['content']

        try:
            users_dict = json.loads(content)
        except:
            users_dict = {}

        users_dict[self.username] = self.password
        updated_content = json.dumps(users_dict, indent=4)

        update_payload = {
            "files": {
                filename: {
                    "content": updated_content
                }
            }
        }
        update_resp = requests.patch(url, headers=headers, json=update_payload)

        if update_resp.status_code == 200:
            button.label = "Approved ✅"
            button.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.send_message(f"✅ Success! **{self.username}** has been approved and added to GitHub.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Failed to update GitHub Gist.", ephemeral=True)

@app.route('/signup', methods=['POST'])
def receive_signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"status": "error", "message": "Missing data"}, 400

    # Post message to Discord channel with the approval button
    async def send_to_discord():
        await client.wait_until_ready()
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            view = ApprovalView(username, password)
            await channel.send(
                content=f"🆕 **NEW SIGN UP REQUEST!**\n🎮 **Game Name:** `{username}`\n🔑 **Game Password:** `{password}`",
                view=view
            )

    client.loop.create_task(send_to_discord())
    return {"status": "success"}, 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

# Start Flask web server in a separate thread so Discord bot and server run together
threading.Thread(target=run_flask).start()

client.run(TOKEN)