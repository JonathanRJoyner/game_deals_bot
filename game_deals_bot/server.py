from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
import os
import asyncio
from discord.ext import commands


load_dotenv()
VOTE_CHANNEL_ID = int(os.getenv('VOTE_CHANNEL_ID'))
TOPGG_AUTH_TOKEN = os.getenv('TOPGG_AUTH_TOKEN')
PORT = int(os.getenv('PORT', 8080))

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    bot = app.config['bot']
    auth_header = request.headers.get('Authorization')

    if auth_header != TOPGG_AUTH_TOKEN:
        return abort(401)  # Unauthorized

    data = request.json
    user_id = data.get('user')
    if user_id:
        channel = app.config['bot'].get_channel(VOTE_CHANNEL_ID)
        if channel:
            asyncio.run_coroutine_threadsafe(send_message(channel, user_id), bot.loop)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "invalid data"}), 400

async def send_message(channel, user_id):
    await channel.send(f"<@{user_id}> voted for Game Deals on top.gg! 🎉")

def run_server(bot: commands.Bot):
    import threading

    app.config['bot'] = bot
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT)).start()