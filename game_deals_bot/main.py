import discord
import api_calls as api_calls
from database import fetch_alerts, delete_alert_row
import ui.embeds as embeds
import ui.views as views
from dotenv import load_dotenv
import bot_tasks
import os
import threading
from server import run_server


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SERVER_COUNT_CHANNEL = os.getenv('SERVER_COUNT_CHANNEL')
TOPGG_API_TOKEN = os.getenv('TOPGG_API_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

# Initialize the bot
bot = discord.AutoShardedBot()

# Error logging
if LOG_CHANNEL_ID:
  @bot.event
  async def on_application_command_error(ctx: discord.ApplicationContext, error):
      log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
      await log_channel.send(f"""
        User: {ctx.user.name} | 
        Command/Button: {ctx.command.name} | 
        Type: {ctx.interaction.type} | 
        Variables: {ctx.interaction.data['options']} | 
        Error: {error}
        """
      )


@bot.event
async def on_ready():
  
  # Starting up tasks
  bot_tasks.check_alerts.start(bot)
  
  # Updating server count channel if it exists
  if SERVER_COUNT_CHANNEL:
    bot_tasks.update_server_count.start(bot, SERVER_COUNT_CHANNEL)
  
  # Updating topgg stats if api token exists
  if TOPGG_API_TOKEN:
    bot_tasks.update_top_gg_server_count.start(bot, TOPGG_API_TOKEN)
  
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
    # Start the Flask app in a separate thread and pass the bot instance to it
    flask_thread = threading.Thread(target=run_server, args=(bot,))
    flask_thread.start()

    # Start the bot
    bot.run(DISCORD_BOT_TOKEN)