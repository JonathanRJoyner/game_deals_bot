import discord
from discord.ext import pages
import api_calls as api_calls
from database import fetch_alerts, delete_alert_row
import ui.embeds as embeds
import ui.views as views
from dotenv import load_dotenv
import bot_tasks
import os
import threading
from database import insert_alert
from ui.modals import PriceAlertModal


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SERVER_COUNT_CHANNEL = os.getenv('SERVER_COUNT_CHANNEL')
TOPGG_API_TOKEN = os.getenv('TOPGG_API_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')
DEBUG = os.getenv('DEBUG')

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
  if not DEBUG:
    bot_tasks.check_free_alerts.start(bot)
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


async def sort_options(ctx: discord.AutocompleteContext):
   return [discord.OptionChoice(name=name, value=value) for name, value 
           in api_calls.sort_values.items()]


async def alert_types(ctx: discord.AutocompleteContext):
   return [discord.OptionChoice(name=name) for name in alert_type_dict]


async def get_alerts(ctx: discord.AutocompleteContext):
    guild_id = str(ctx.interaction.guild_id)
    alerts = await fetch_alerts(guild_id)
    
    options = [
        discord.OptionChoice(
          name=f"Title: {alert['game_title']} | Type: {alert['alert_type']} | Target: {alert['target_price']}"[0:100], 
          value=f"{alert['id']}_{alert['game_title']}"
        )
        for alert in alerts
    ]
    return options


@bot.slash_command(name="price", description="Get the current price overview of a game.")
async def price(
	ctx: discord.ApplicationContext,
	game_title: discord.Option(
    	str,
        description="Select a game title.",
    	autocomplete=discord.utils.basic_autocomplete(get_game_title)
	)# type: ignore
):
  game_id = game_title.split('_')[1]
  game_title = game_title.split('_')[0]

  embed = await embeds.price_overview_embed(game_id)
  
  view = await views.price_overview_view(ctx.interaction, game_id, game_title)
  await ctx.respond(embed=embed, view=view)


@bot.slash_command(name="deals",  description="View the latest game deals sorted by various options.")
async def deals(
  ctx: discord.ApplicationContext,
    sort_by: discord.Option(
        str,
        description="Choose a sorting method.",
        autocomplete=discord.utils.basic_autocomplete(sort_options)
    )  # type: ignore
):
  await ctx.response.defer()
  embed_list = await embeds.deals_list_embed(sort_by)
  await pages.Paginator(pages=embed_list).respond(ctx.interaction)


@bot.slash_command(name="delete_alert", description="Delete a price alert from the server.")
async def delete_alert_command(
    ctx: discord.ApplicationContext,
    alert: discord.Option(
        str,
        description="Select the alert to delete.",
        autocomplete=discord.utils.basic_autocomplete(get_alerts)
    )  # type: ignore
):
  alert_id = alert.split('_')[0]
  alert_title = alert.split('_')[1]
  
  # Delete the alert
  await delete_alert_row(alert_id)
  
  await ctx.respond(
    f"Alert for {alert_title} has been successfully deleted.", 
    ephemeral=True
  )


@bot.slash_command(name="free_game_alert", description="Set an alert for when any game becomes free.")
async def free_game_alert(ctx: discord.ApplicationContext):
  resp = await insert_alert(
    user_id=ctx.user.id,
    guild_id=ctx.guild.id,
    channel_id=ctx.channel.id,
    target_price=0,
    game_id=None,
    game_title=None,
    alert_type='Free Game Alert'
  )

  if resp.data:
      await ctx.respond("Alert added successfully!", ephemeral=True)
  else:
      await ctx.respond("An error occured setting the alert.", ephemeral=True)


alert_type_dict= [
    'Price Alert',
    'Price Drop Alert',
    'All Time Low Price Alert',
    '3 Month Low Price Alert'
]

@bot.slash_command(name="set_price_alert", description="Set various types of price alerts for a specific game.")
async def set_price_alert(
	ctx: discord.ApplicationContext,
    alert_type: discord.Option(
        str,
        description="Choose the type of price alert.",
        autocomplete=discord.utils.basic_autocomplete(alert_types)
    ),  # type: ignore
    game_title: discord.Option(
        str,
        description="Select a game title.",
        autocomplete=discord.utils.basic_autocomplete(get_game_title)
    )  # type: ignore
):
	game_id = game_title.split('_')[1]
	game_title = game_title.split('_')[0]
	if alert_type == 'Price Alert':
		await ctx.interaction.response.send_modal(
            PriceAlertModal(game_id, game_title)
        )

	else:
		resp = await insert_alert(
			user_id=ctx.user.id,
			guild_id=ctx.guild.id,
			channel_id=ctx.channel.id,
			target_price=0,
			game_id=game_id,
			game_title=game_title,
			alert_type=alert_type
		)

		if resp.data:
			await ctx.respond(f"{alert_type} for {game_title} added successfully!", ephemeral=True)
		else:
			await ctx.respond("An error occured setting the alert.", ephemeral=True)



if __name__ == '__main__':
	bot.run(DISCORD_BOT_TOKEN)