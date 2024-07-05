from database import fetch_rows_in_batches, delete_alert_row
from discord.ext import tasks, commands
from api_calls import fetch_game_price_overview, fetch_deals, fetch_price_history
from ui.embeds import price_overview_embed
import aiohttp
from database import fetch_free_game_alerts
from models import price_history
import discord
from datetime import datetime
import os

seen_ids = set()

LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

async def send_log(bot: commands.Bot, message: str):
    log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
    if log_channel:
        await log_channel.send(message)
    else:
        print(f"Log channel not found: {message}")


@tasks.loop(hours=12)
async def check_alerts(bot: commands.Bot):
    await send_log(bot, f"Starting check_alerts")
    async for batch in fetch_rows_in_batches():
        ids = [row['game_id'] for row in batch]
        response = await fetch_game_price_overview(ids=ids)

        for row in batch:
            game_id = row['game_id']
            target_price = row['target_price']
            row_id = row['id']
            alert_type = row['alert_type']

            try:
                if alert_type == 'Price Alert':
                    for price in response['prices']:
                        if price['id'] == game_id and price['current']['price']['amount'] < target_price:
                            channel_id = row['channel_id']
                            channel = bot.get_channel(channel_id)
                            header_embed = discord.Embed(title='__Price Alert__', color=discord.Color.red())
                            embed = await price_overview_embed(game_id)
                            embed.color = discord.Color.red()

                            await channel.send(embeds=[header_embed, embed])
                            await delete_alert_row(row_id)
                            await send_log(bot, f"Price Alert sent for game ID {game_id} in channel {channel_id}")

                elif alert_type == 'All Time Low Price Alert':
                    for price in response['prices']:
                        if price['id'] == game_id and price['lowest']['price']['amount'] >= price['current']['price']['amount']:
                            channel_id = row['channel_id']
                            channel = bot.get_channel(channel_id)
                            header_embed = discord.Embed(title='__All Time Low Price Alert__', color=discord.Color.red())
                            embed = await price_overview_embed(game_id)
                            embed.color = discord.Color.red()

                            await channel.send(embeds=[header_embed, embed])
                            await delete_alert_row(row_id)
                            await send_log(bot, f"All Time Low Price Alert sent for game ID {game_id} in channel {channel_id}")

                elif alert_type == 'Price Drop Alert':
                    data = await fetch_price_history(game_id)
                    data = await price_history.from_json(data)
                    data = sorted(data, key=lambda x: x.timestamp)
                    today = datetime.now(data[-1].timestamp.tzinfo).date()
                    if data[-1].timestamp.date() == today:
                        price_today = data[-1].deal.price.amount
                        previous_price = next((record.deal.price.amount for record in data if record.timestamp.date() != today), None)

                        if price_today < previous_price:
                            channel_id = row['channel_id']
                            channel = bot.get_channel(channel_id)
                            header_embed = discord.Embed(title='__Price Drop Alert__', color=discord.Color.red())
                            embed = await price_overview_embed(game_id)
                            embed.color = discord.Color.red()

                            await channel.send(embeds=[header_embed, embed])
                            await delete_alert_row(row_id)
                            await send_log(bot, f"Price Drop Alert sent for game ID {game_id} in channel {channel_id}")

                elif alert_type == '3 Month Low Price Alert':
                    data = await fetch_price_history(game_id)
                    data = await price_history.from_json(data)
                    data = sorted(data, key=lambda x: x.timestamp)
                    today = datetime.now(data[-1].timestamp.tzinfo).date()
                    if data[-1].timestamp.date() == today:
                        price_today = data[-1].deal.price.amount
                        all_prices = [record.deal.price.amount for record in data]

                        if price_today <= min(all_prices):
                            channel_id = row['channel_id']
                            channel = bot.get_channel(channel_id)
                            header_embed = discord.Embed(title='__3 Month Low Price Alert__', color=discord.Color.red())
                            embed = await price_overview_embed(game_id)
                            embed.color = discord.Color.red()

                            await channel.send(embeds=[header_embed, embed])
                            await delete_alert_row(row_id)
                            await send_log(bot, f"3 Month Low Price Alert sent for game ID {game_id} in channel {channel_id}")

            except Exception as e:
                await send_log(bot, f"Failed to process alert for game ID {game_id}: {e}")
                continue


@tasks.loop(hours=6)
async def check_free_alerts(bot: commands.Bot):
    global seen_ids

    await send_log(bot, f"Starting check_free_alerts")
    
    try:
        data = await fetch_deals('price')
        current_ids = set(item['id'] for item in data['list'] if item['deal']['price']['amount'] == 0)

        if not seen_ids:
            seen_ids = current_ids

        else:
            new_ids = current_ids - seen_ids
            embeds = [discord.Embed(title='Free Games')]
            for id in new_ids:
                embed = await price_overview_embed(id)
                embed.color = discord.Color.red()
                embeds.append(embed)

            channels = await fetch_free_game_alerts()
            for channel in channels:
                channel_id = channel['channel_id']
                channel = bot.get_channel(channel_id)
                await channel.send(embeds=embeds)
                await send_log(bot, f"Sent Free Game Alerts for new IDs: {new_ids} in channel {channel_id}")

            seen_ids.update(current_ids)

    except Exception as e:
        await send_log(bot, f"Failed to check free alerts: {e}")


@tasks.loop(hours=6)
async def update_server_count(bot: commands.Bot, server_count_channel: int):
    server_count_channel_id = int(server_count_channel)
    server_count_channel = bot.get_channel(server_count_channel_id)
    server_count = len(bot.guilds)
    shard_count = int(bot.shard_count)
    await server_count_channel.edit(
        name=f"SERVERS: {server_count} SHARDS: {shard_count}"
    )


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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                print("Successfully updated server count on top.gg")
            else:
                print(f"Failed to update server count on top.gg: {response.status}")