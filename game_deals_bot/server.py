from dotenv import load_dotenv
import os
from flask import request, jsonify
from main import app, bot
import asyncio

load_dotenv()
VOTE_CHANNEL_ID = os.getenv('VOTE_CHANNEL_ID')

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)
    user_id = data.get('user')
    if user_id:
        channel = bot.get_channel(VOTE_CHANNEL_ID)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(f"User <@{user_id}> has voted for the bot on top.gg! 🎉"), bot.loop)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "invalid data"}), 400