import discord
from discord.ui import Button, View
import api_calls
from models import price_history, price_overview, info
from textwrap import dedent
from ui.modals import PriceAlertModal
import ui.graphs as graphs


async def alert_callback(interaction: discord.Interaction, id: str, title: str):
    await interaction.response.send_modal(PriceAlertModal(id, title))


async def history_button_callback(interaction: discord.Interaction):
    id = interaction.data['custom_id']
    data = await api_calls.fetch_price_history(id)
    data = await price_history.from_json(data)
    graph = await graphs.history_graph(data)
    file = discord.File(fp=graph, filename='graph.png')

    # Retrieve the original embed
    original_embed = interaction.message.embeds[0]

    # Set the image of the original embed
    original_embed.set_image(url="attachment://graph.png")

    # Edit the original message with the updated embed
    await interaction.message.edit(embed=original_embed)
    
    # Send the file separately
    await interaction.followup.send(file=file)
    

async def more_info_callback(interaction: discord.Interaction, id: str):
    info_json = await api_calls.fetch_game_info(id)

    game_info = await info.from_json(info_json)

    embed = interaction.message.embeds[0]

    # Adding an empty field to create a new row
    embed.add_field(
        name='\u200b',
        value='\u200b',
        inline=False
    )

    # Reviews Field
    if game_info.reviews:
        reviews_text = '\n'.join(
            [f"{review.source}: `{review.score} ({review.count} reviews)`" for review in game_info.reviews]
        )
        embed.add_field(
            name='Reviews',
            value=dedent(reviews_text),
            inline=False
        )

    # Players Field
    if game_info.players:
        players_info = dedent('\n'.join(
            [f"{attr.capitalize()}: `{getattr(game_info.players, attr)}`" for attr in ['recent', 'day', 'week', 'peak'] if getattr(game_info.players, attr) is not None]
        ))
        embed.add_field(
            name='Players',
            value=players_info,
        )

    # Stats Field
    if game_info.stats:
        stats_info = dedent('\n'.join(
            [f"{attr.capitalize()}: `{getattr(game_info.stats, attr)}`" for attr in ['rank', 'waitlisted', 'collected'] if getattr(game_info.stats, attr) is not None]
        ))
        embed.add_field(
            name='Stats',
            value=stats_info,
        )

    # Adding an empty field to create a new row
    embed.add_field(
        name='\u200b',
        value='\u200b',
        inline=False
    )

    # Developers Field
    if game_info.developers:
        developers_text = '\n'.join(
            [f"`{dev.name}`" for dev in game_info.developers if dev.name]
        )
        embed.add_field(
            name='Developers',
            value=dedent(developers_text),
        )

    # Publishers Field
    if game_info.publishers:
        publishers_text = '\n'.join(
            [f"`{pub.name}`" for pub in game_info.publishers if pub.name]
        )
        embed.add_field(
            name='Publishers',
            value=dedent(publishers_text),
        )

    # Disable the More Info button
    view = await price_overview_view(interaction, id, game_info.title)
    for item in view.children:
        if isinstance(item, discord.ui.Button) and item.label == "More Info":
            item.disabled = True

    await interaction.response.edit_message(embed=embed, view=view)



async def price_overview_view(interaction: discord.Interaction, id: str, title: str) -> View:
    
    view = View(timeout=30.0)

    # Alert Button
    alert_button = Button(label="Alert", style=discord.ButtonStyle.red)
    alert_button.callback = lambda interaction: alert_callback(interaction, id, title)
    view.add_item(alert_button)

    # History Button
    history_button = Button(
        label="History", 
        style=discord.ButtonStyle.primary, 
        custom_id=id
    )
    history_button.callback = history_button_callback
    view.add_item(history_button)

    # More Info Button
    more_info_button = Button(
        label="More Info", 
        style=discord.ButtonStyle.green,
        custom_id='More Info'
    )
    more_info_button.callback = lambda interaction: more_info_callback(interaction, id)
    view.add_item(more_info_button)

    # Setting the timeout callback
    async def on_timeout():
        for item in view.children:
            item.disabled = True
        await interaction.edit_original_response(view=view)
    view.on_timeout = on_timeout
    
    return view

