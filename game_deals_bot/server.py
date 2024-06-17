from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import asyncio
from discord.ext import commands


load_dotenv()
VOTE_CHANNEL_ID = int(os.getenv('VOTE_CHANNEL_ID'))
PORT = int(os.getenv('PORT', 8080))

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    bot = app.config['bot']
    data = request.json
    print(data)
    user_id = data.get('user')
    if user_id:
        channel = app.config['bot'].get_channel(VOTE_CHANNEL_ID)
        if channel:
            asyncio.run_coroutine_threadsafe(send_message(channel, user_id), bot.loop)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "invalid data"}), 400

async def send_message(channel, user_id):
    await channel.send(f"User <@{user_id}> has voted for the bot on top.gg! 🎉")

def run_server(bot: commands.Bot):
    import threading

    app.config['bot'] = bot
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()