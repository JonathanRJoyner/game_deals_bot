from database import fetch_rows_in_batches, delete_alert_row
from discord.ext import tasks, commands
from api_calls import fetch_game_price_overview
from ui.embeds import price_overview_embed
from dotenv import load_dotenv
import os
import aiohttp
import server

load_dotenv()
SERVER_COUNT_CHANNEL = os.getenv('SERVER_COUNT_CHANNEL')
TOPGG_API_TOKEN = os.getenv('TOPGG_API_TOKEN')


@tasks.loop(hours=1)
async def check_alerts(bot: commands.Bot):
    async for batch in fetch_rows_in_batches():

        # Getting price data
        ids = [row['game_id'] for row in batch]
        response = await fetch_game_price_overview(ids=ids)

        # Sending alerts if price is below target
        for row in batch:
            game_id = row['game_id']
            target_price = row['target_price']
            row_id = row['id']

            for price in response['prices']:
                if price['id'] == game_id and price['current']['price']['amount'] < target_price:
                    channel_id = row['channel_id']
                    channel = bot.get_channel(channel_id)
                    embed = await price_overview_embed(game_id)

                    # Modifying Embed
                    embed.insert_field_at(
                        index=0,
                        name='__**Alert Target Price**__',
                        value=f'{target_price}',
                        inline=False
                    )
                    embed.color = embed.color.red()
                    embed.title = f'Price Alert: {embed.title}'

                    # Sending Alert
                    await channel.send(embed=embed)

                    # Deleting Row
                    await delete_alert_row(row_id)
                    

@tasks.loop(hours=6)
async def update_server_count(bot: commands.Bot):
    server_count_channel_id = int(os.getenv('SERVER_COUNT_CHANNEL'))
    server_count_channel = bot.get_channel(server_count_channel_id)
    if server_count_channel is None:
        print(f"Channel with ID {server_count_channel_id} not found.")
        return
    
    server_count = len(bot.guilds)
    await server_count_channel.edit(name=f"SERVER COUNT: {server_count}")


@tasks.loop(hours=6)
async def update_top_gg_server_count(bot: commands):
    url = f"https://top.gg/api/bots/{bot.user.id}/stats"
    headers = {
        "Authorization": TOPGG_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    server_count = len(bot.guilds)
    shard_count = bot.shard_count

    payload = {
        "server_count": server_count,
        "shard_count": shard_count,
        "shards": [bot.get_shard(i).id for i in range(shard_count)]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                print("Successfully updated server count on top.gg")
            else:
                print(f"Failed to update server count on top.gg: {response.status}")
                