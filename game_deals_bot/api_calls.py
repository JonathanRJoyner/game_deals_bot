import aiohttp
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

ITAD_KEY = os.getenv('ITAD_KEY')

search_base_url = 'https://api.isthereanydeal.com/games/search/v1'
info_base_url = 'https://api.isthereanydeal.com/games/info/v2'
price_base_url = 'https://api.isthereanydeal.com/games/prices/v2'
price_overview_base_url = 'https://api.isthereanydeal.com/games/overview/v2'
history_url = 'https://api.isthereanydeal.com/games/history/v2'

params = {'key': ITAD_KEY}

async def api_call(url, params, body = None, method="GET"):
    async with aiohttp.ClientSession() as session:
        if method == 'GET':
            async with session.get(url, params=params) as response:
                return await response.json()
        
        elif method == 'POST':
            async with session.post(url, params=params, json=body) as response:
                return await response.json()


async def fetch_search_results(title: str) -> dict:
    params['title'] = title
    resp = await api_call(search_base_url, params)
    return resp


async def fetch_game_info(id: str) -> dict:
    params['id'] = id
    resp = await api_call(info_base_url, params)
    return resp


async def fetch_game_price_overview(id: str = None, ids: List[str] = None) -> dict:
    
    if id:
        body = [id]
    elif ids:
        body = ids
    else:
        raise AttributeError('Need id or ids')
    
    
    resp = await api_call(
        price_overview_base_url, 
        params=params, 
        body = body, 
        method = 'POST'
    )
    return resp


async def fetch_price_history(id: str) -> dict:
    params['id'] = id
    resp = await api_call(
        history_url,
        params=params
    )
    return resp