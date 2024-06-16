import json
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

# Define the classes to match the JSON structure
@dataclass
class Shop:
    id: int
    name: str

@dataclass
class Price:
    amount: float
    amountInt: int
    currency: str

@dataclass
class Platform:
    id: int
    name: str

@dataclass
class Current:
    shop: Shop
    price: Price
    regular: Price
    cut: int
    voucher: Optional[str]
    flag: Optional[str]
    drm: List[str]
    platforms: List[Platform]
    timestamp: datetime
    expiry: Optional[str]
    url: str

@dataclass
class Lowest:
    shop: Shop
    price: Price
    regular: Price
    cut: int
    timestamp: datetime

@dataclass
class PriceData:
    id: str
    current: Current
    lowest: Lowest
    bundled: int
    urls: Dict[str, str]

@dataclass
class Game:
    id: str
    slug: str
    title: str
    type: str
    mature: bool

@dataclass
class Tier:
    price: Price
    games: List[Game]

@dataclass
class Page:
    id: int
    name: str
    shopId: int

@dataclass
class Bundle:
    id: int
    title: str
    page: Page
    url: str
    details: str
    isMature: bool
    publish: datetime
    expiry: datetime
    counts: Dict[str, int]
    tiers: List[Tier]


async def from_json(data: dict) -> Tuple[List[PriceData], List[Bundle]]:

    prices = []
    for price in data['prices']:
        current_expiry = datetime.fromisoformat(price['current']['expiry']) if price['current']['expiry'] else None
        current = Current(
            shop=Shop(**price['current']['shop']),
            price=Price(**price['current']['price']),
            regular=Price(**price['current']['regular']),
            cut=price['current']['cut'],
            voucher=price['current']['voucher'],
            flag=price['current']['flag'],
            drm=price['current']['drm'],
            platforms=[Platform(**platform) for platform in price['current']['platforms']],
            timestamp=datetime.fromisoformat(price['current']['timestamp']),
            expiry=current_expiry,
            url=price['current']['url']
        )
        lowest = Lowest(
            shop=Shop(**price['lowest']['shop']),
            price=Price(**price['lowest']['price']),
            regular=Price(**price['lowest']['regular']),
            cut=price['lowest']['cut'],
            timestamp=datetime.fromisoformat(price['lowest']['timestamp'])
        )
        price_data = PriceData(
            id=price['id'],
            current=current,
            lowest=lowest,
            bundled=price['bundled'],
            urls=price['urls']
        )
        prices.append(price_data)

    bundles = []
    for bundle in data['bundles']:
        page = Page(**bundle['page'])
        tiers = [Tier(
            price=Price(**tier['price']) if tier.get('price') else None,
            games=[Game(**game) for game in tier['games']]
        ) for tier in bundle['tiers']]
        bundle_obj = Bundle(
            id=bundle['id'],
            title=bundle['title'],
            page=page,
            url=bundle['url'],
            details=bundle['details'],
            isMature=bundle['isMature'],
            publish=datetime.fromisoformat(bundle['publish']),
            expiry=datetime.fromisoformat(bundle['expiry']),
            counts=bundle['counts'],
            tiers=tiers
        )
        bundles.append(bundle_obj)

    return prices, bundles