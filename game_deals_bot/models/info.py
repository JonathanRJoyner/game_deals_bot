import json
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Asset:
    boxart: Optional[str] = None
    banner145: Optional[str] = None
    banner300: Optional[str] = None
    banner400: Optional[str] = None
    banner600: Optional[str] = None

@dataclass
class Developer:
    id: Optional[int] = None
    name: Optional[str] = None

@dataclass
class Publisher:
    id: Optional[int] = None
    name: Optional[str] = None

@dataclass
class Review:
    score: Optional[int] = None
    source: Optional[str] = None
    count: Optional[int] = None
    url: Optional[str] = None

@dataclass
class Stats:
    rank: Optional[int] = None
    waitlisted: Optional[int] = None
    collected: Optional[int] = None

@dataclass
class Players:
    recent: Optional[int] = None
    day: Optional[int] = None
    week: Optional[int] = None
    peak: Optional[int] = None

@dataclass
class Urls:
    game: Optional[str] = None

@dataclass
class GameInfo:
    id: str
    slug: str
    title: str
    type: str
    mature: bool
    assets: Optional[Asset]
    earlyAccess: Optional[bool]
    achievements: Optional[bool]
    tradingCards: Optional[bool]
    appid: Optional[int]
    tags: Optional[List[str]]
    releaseDate: Optional[datetime]
    developers: Optional[List[Developer]]
    publishers: Optional[List[Publisher]]
    reviews: Optional[List[Review]]
    stats: Optional[Stats]
    players: Optional[Players]
    urls: Optional[Urls]

async def from_json(data: Dict) -> GameInfo:
    game_info = GameInfo(
        id=data.get('id'),
        slug=data.get('slug'),
        title=data.get('title'),
        type=data.get('type'),
        mature=data.get('mature'),
        assets=Asset(**data['assets']) if data.get('assets') else None,
        earlyAccess=data.get('earlyAccess'),
        achievements=data.get('achievements'),
        tradingCards=data.get('tradingCards'),
        appid=data.get('appid'),
        tags=data.get('tags'),
        releaseDate=datetime.fromisoformat(data['releaseDate']) if data.get('releaseDate') else None,
        developers=[Developer(**dev) for dev in data.get('developers', [])] if data.get('developers') else None,
        publishers=[Publisher(**pub) for pub in data.get('publishers', [])] if data.get('publishers') else None,
        reviews=[Review(**rev) for rev in data.get('reviews', [])] if data.get('reviews') else None,
        stats=Stats(**data['stats']) if data.get('stats') else None,
        players=Players(**data['players']) if data.get('players') else None,
        urls=Urls(**data['urls']) if data.get('urls') else None
    )
    return game_info
