from database import fetch_rows_in_batches, delete_alert_row
from discord.ext import tasks, commands
from api_calls import fetch_game_price_overview, fetch_deals
from ui.embeds import price_overview_embed
import aiohttp
from database import fetch_free_game_alerts
import discord

seen_ids = set()

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

@tasks.loop(hours=1)
async def check_free_alerts(bot: commands.Bot):
    global seen_ids
    
    # Fetch the current deals
    data = await fetch_deals('price')
    current_ids = set(item['id'] for item in data['list'] if item['deal']['price']['amount'] == 0)

    # If this is the first run, initialize seen_ids without comparison
    if not seen_ids:
        seen_ids = current_ids

    else:
        # Compare the current IDs with the previously seen IDs
        new_ids = current_ids - seen_ids

        # If there are new deals, create embeds
        embeds = [discord.Embed(title='Free Games')]
        for id in new_ids:
            embed = await price_overview_embed(id)
            embed.color = embed.color.red()
            embeds.append(embed)
            channels = await fetch_free_game_alerts()

        # Sending embeds
        for channel in channels:
            channel_id = channel['channel_id']
            channel = bot.get_channel(channel_id)
            await channel.send(embeds=embeds)

        # Update seen_ids with the current IDs
        seen_ids.update(current_ids)


@tasks.loop(hours=6)
async def update_server_count(bot: commands.Bot, server_count_channel: int):
    server_count_channel_id = int(server_count_channel)
    server_count_channel = bot.get_channel(server_count_channel_id)
    if server_count_channel is None:
        print(f"Channel with ID {server_count_channel_id} not found.")
        return
    
    server_count = len(bot.guilds)
    await server_count_channel.edit(name=f"SERVER COUNT: {server_count}")


@tasks.loop(hours=6)
async def update_top_gg_server_count(bot: commands, topgg_api_token: str):
    url = f"https://top.gg/api/bots/{bot.user.id}/stats"
    headers = {
        "Authorization": topgg_api_token,
        "Content-Type": "application/json"
    }    

    payload = {
        "server_count": int(len(bot.guilds)),
        "shard_count": int(bot.shard_count),
    }
    print(payload)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                print("Successfully updated server count on top.gg")
            else:
                print(f"Failed to update server count on top.gg: {response.status}")
                