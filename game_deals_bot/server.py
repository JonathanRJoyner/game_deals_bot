from aiohttp import web
from dotenv import load_dotenv
import os

load_dotenv()
VOTE_CHANNEL_ID = os.getenv('VOTE_CHANNEL_ID')


# Webhook server setup
async def handle_vote(request):
    from main import bot
    data = await request.json()
    user_id = data.get('user')
    
    if user_id:
        channel = bot.get_channel(VOTE_CHANNEL_ID)
        if channel:
            await channel.send(f"User <@{user_id}> has voted for the bot on top.gg! 🎉")
        return web.Response(status=200, text="Vote received")
    return web.Response(status=400, text="Invalid data")

# Function to run the webhook server
async def run_webhook():
    app = web.Application()
    app.router.add_post('/webhook', handle_vote)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=8080)
    await site.start()
    print('Webhook server running')
    