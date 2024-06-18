import discord
from textwrap import dedent
import api_calls as api_calls
from models import info, price_overview
from typing import List
import asyncio


async def price_overview_embed(id: str) -> discord.Embed:
    price_json = await api_calls.fetch_game_price_overview(id=id)
    info_json = await api_calls.fetch_game_info(id)

    prices, bundles = await price_overview.from_json(price_json)
    game_info = await info.from_json(info_json)

    # Default values in case assets or urls are None
    banner300_url = game_info.assets.banner300 if game_info.assets else None
    game_url = game_info.urls.game if game_info.urls else None

    # Convert expiry and timestamp to Unix timestamps
    current_expiry_unix = int(prices[0].current.expiry.timestamp()) if prices[0].current.expiry else None
    lowest_timestamp_unix = int(prices[0].lowest.timestamp.timestamp()) if prices[0].lowest.timestamp else None

    embed = discord.Embed(
        title=f'{game_info.title}',
        url=game_url,
        color=discord.Color.dark_green()
    )

    if banner300_url:
        embed.set_image(url=banner300_url)

    if prices:
        # Current Prices Field
        current_expiry_unix = f'<t:{current_expiry_unix}:R>' if current_expiry_unix else '`N/A`'
        embed.add_field(
            name='Current', 
            value=dedent(f'''
                Price: `{prices[0].current.price.amount} {prices[0].current.price.currency}`
                Discount: `-{prices[0].current.cut}%`
                Shop: [{prices[0].current.shop.name}]({prices[0].current.url})
                Expires: {current_expiry_unix}
            '''),
        )

        # Lowest Prices Field
        lowest_timestamp_unix = f'<t:{lowest_timestamp_unix}:R>' if lowest_timestamp_unix else '`N/A`'
        embed.add_field(
            name='Lowest', 
            value=dedent(f'''
                Price: `{prices[0].lowest.price.amount} {prices[0].lowest.price.currency}`
                Discount: `-{prices[0].lowest.cut}%`
                Shop: `{prices[0].lowest.shop.name}`
                Expired: {lowest_timestamp_unix}
            ''')
        )


    # Footer
    embed.set_footer(
        icon_url='https://isthereanydeal.com/favicon.png',
        text='Powered by ITAD'
    )
    return embed


async def deals_list_embed(sort: str) -> List[discord.Embed]:
    data = await api_calls.fetch_deals(sort)
    ids = [item['id'] for item in data['list']]
    embeds = []
    for id in ids:
        embed = await price_overview_embed(id)
        embeds.append(embed)
        await asyncio.sleep(1)  # Rate limit to once per second
    return embeds