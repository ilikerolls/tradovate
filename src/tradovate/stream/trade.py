## Imports
from __future__ import annotations

from .client import Client
from src.config import to_auth_dict


class TradOvate(Client):
    """ Tradovate Client"""

    async def on_subcribe(self, ticker, interval) -> None:
        await self.subscribe_symbol(ticker, interval=interval, total=240)

    async def on_unsubcribe(self, ticker) -> None:
        await self.unsubscribe_symbol(ticker)


def subcribe(ticker, interval):
    client = TradOvate()
    client.run_subcribe(to_auth_dict, ticker=ticker, interval=interval)


def run():
    client = TradOvate()
    client.run(to_auth_dict, ticker='ESU2', interval=5)
