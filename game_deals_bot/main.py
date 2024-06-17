import discord
import api_calls as api_calls
from database import fetch_alerts, delete_alert_row
import ui.embeds as embeds
import ui.views as views
from dotenv import load_dotenv
import bot_tasks
import os
import asyncio
import server
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Initialize the bot
bot = discord.AutoShardedBot()

@bot.event
async def on_ready():
  
  # Starting up tasks
  bot_tasks.check_alerts.start(bot)
  bot_tasks.update_server_count.start(bot)
  bot_tasks.update_top_gg_server_count.start(bot)
  bot.loop.create_task(server.run_webhook(bot))
  
  print(f'Logged in as {bot.user}')


async def get_game_title(ctx: discord.AutocompleteContext):
  game_title = ctx.options['game_title']
  resp = await api_calls.fetch_search_results(game_title)
  options = [
    discord.OptionChoice(name=item['title'], value=f'{item["title"]}_{item["id"]}')
    for item in resp
  ]
  return options


async def get_alerts(ctx: discord.AutocompleteContext):
    guild_id = str(ctx.interaction.guild_id)
    alerts = await fetch_alerts(guild_id)
    
    options = [
        discord.OptionChoice(
          name=f"Title: {alert['game_title']} Target: {alert['target_price']}"[0:100], 
          value=f"{alert['id']}_{alert['game_title']}"
        )
        for alert in alerts
    ]
    return options


@bot.slash_command(name="price")
async def price(
  ctx: discord.ApplicationContext,
  game_title: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_game_title)) # type: ignore
):
  game_id = game_title.split('_')[1]
  game_title = game_title.split('_')[0]

  embed = await embeds.price_overview_embed(game_id)
  
  
  view = await views.price_overview_view(ctx.interaction, game_id, game_title)
  await ctx.respond(embed=embed, view=view)


@bot.slash_command(name="delete_alert")
async def delete_alert_command(
    ctx: discord.ApplicationContext,
    alert: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_alerts)) # type: ignore
):
  alert_id = alert.split('_')[0]
  alert_title = alert.split('_')[1]
  
  # Delete the alert
  await delete_alert_row(alert_id)
  
  await ctx.respond(
    f"Alert for {alert_title} has been successfully deleted.", 
    ephemeral=True
  )


if __name__ == '__main__':
    # Start the bot in a separate thread
    import threading
    threading.Thread(target=bot.run, args=(TOKEN,), daemon=True).start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))