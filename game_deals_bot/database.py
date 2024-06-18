from supabase import create_client, Client
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def insert_alert(
        user_id: int, 
        guild_id: int, 
        channel_id: int, 
        target_price: float, 
        game_id: str,
        game_title
):
    data = {
        "user_id": user_id,
        "guild_id": guild_id,
        "target_price": target_price,
        "game_id": game_id,
        "channel_id": channel_id,
        "game_title": game_title
    }
    response = await asyncio.to_thread(supabase.table('alerts').insert(data).execute)
    return response


async def fetch_rows_in_batches(batch_size: int = 5):
    offset = 0
    while True:
        response = await asyncio.to_thread(supabase.table('alerts').select('*').range(offset, offset + batch_size - 1).execute)
        if response.data:
            yield response.data
            offset += batch_size
        else:
            break


async def delete_alert_row(row_id: str) -> None:
    await asyncio.to_thread(supabase.table('alerts').delete().eq('id', row_id).execute)


async def fetch_alerts(guild_id: str):
    response = await asyncio.to_thread(supabase.from_('alerts').select('*').eq('guild_id', guild_id).execute)
    return response.data


async def fetch_free_game_alerts():
    response = await asyncio.to_thread(supabase.from_('alerts').select('channel_id').eq('game_id', 'free').execute)
    return response.data


async def count_alerts_for_guild(guild_id: int) -> int:
    response = await asyncio.to_thread(supabase.table('alerts').select('id').eq('guild_id', guild_id).execute)
    return len(response.data)