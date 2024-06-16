from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Price:
    amount: float
    amountInt: int
    currency: str

@dataclass
class Deal:
    price: Price
    regular: Price
    cut: int

@dataclass
class Shop:
    id: int
    name: str

@dataclass
class DealRecord:
    timestamp: datetime
    shop: Shop
    deal: Deal


async def from_json(data: dict) -> List[DealRecord]:
    records = []
    for item in data:
        timestamp = datetime.fromisoformat(item['timestamp'])
        shop = Shop(id=item['shop']['id'], name=item['shop']['name'])
        price = Price(**item['deal']['price'])
        regular = Price(**item['deal']['regular'])
        deal = Deal(price=price, regular=regular, cut=item['deal']['cut'])
        records.append(DealRecord(timestamp=timestamp, shop=shop, deal=deal))
    return records