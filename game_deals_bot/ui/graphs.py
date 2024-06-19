import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import io
from typing import List
from models.price_history import DealRecord
from datetime import timedelta, datetime, timezone
import copy
from dateutil.relativedelta import relativedelta

async def history_graph(data: List[DealRecord]):
    plt.style.use('_mpl-gallery')

    # Filter to the latest 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Add starting point
    highest_timestamp = max(data, key=lambda x: x.timestamp)
    end_point = copy.deepcopy(highest_timestamp)
    end_point.timestamp = datetime.now()
    data.append(end_point)

    # Prepare data for plotting
    timestamps = [item.timestamp for item in data]
    prices = [item.deal.price.amount for item in data]
    regular_prices = [item.deal.regular.amount for item in data]
    currency = data[0].deal.price.currency if data else 'USD'

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.step(timestamps, prices, where='pre', linewidth=2.0, label='Deal Price', marker='o')
    ax.step(timestamps, regular_prices, where='pre', linewidth=2.0, label='Regular Price', linestyle='--')

    # Set the x-axis to show dates within the last three months
    ax.set_xlim(start_date, end_date)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    ax.set_xlabel('Date')
    ax.set_ylabel(f'Price ({currency})')
    ax.set_title(f'Price History')
    ax.legend()

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer
