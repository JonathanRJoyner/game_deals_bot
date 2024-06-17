from aiohttp import web
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()
VOTE_CHANNEL_ID = os.getenv('VOTE_CHANNEL_ID')
PORT = int(os.getenv('PORT', 8080))


# Webhook server setup
async def handle_vote(request, bot: commands.Bot):
    data = await request.json()
    user_id = data.get('user')
    print(user_id)
    
    if user_id:
        channel = bot.get_channel(VOTE_CHANNEL_ID)
        print(channel.id)
        if channel:
            await channel.send(f"User <@{user_id}> has voted for the bot on top.gg! 🎉")
        return web.Response(status=200, text="Vote received")
    return web.Response(status=400, text="Invalid data")

# Function to run the webhook server
async def run_webhook(bot: commands.Bot):
    app = web.Application()
    app.router.add_post('/webhook', lambda request: handle_vote(request, bot))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
    await site.start()
    print(f"Webhook server running on port {PORT}")    