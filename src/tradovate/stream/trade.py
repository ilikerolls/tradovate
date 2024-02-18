## Imports
from __future__ import annotations

from .client import Client
from src.tradovate.config import to_auth_dict, logger


class TradOvate(Client):
    """ Tradovate Client"""

    async def on_subcribe(self, ticker, interval) -> None:
        await self.subscribe_symbol(ticker, interval=interval, total=240)

    async def on_unsubcribe(self, ticker) -> None:
        await self.unsubscribe_symbol(ticker)


def subcribe(ticker, interval):
    client = TradOvate()

    # authorization_dict = {
    #     "name": os.getenv('TO_NAME'),
    #     "password": os.getenv('TO_PASSWORD'),
    #     "appId": os.getenv('TO_APPID'),
    #     "appVersion": "1.0",
    #     "cid": os.getenv('TO_CID'),
    #     "sec": os.getenv('TO_SEC')
    # }
    client.run_subcribe(to_auth_dict, ticker=ticker, interval=interval)


def run():
    client = TradOvate()

    # authorization_dict = {
    #     "name": os.getenv('TO_NAME'),
    #     "password": os.getenv('TO_PASSWORD'),
    #     "appId": os.getenv('TO_APPID'),
    #     "appVersion": "1.0",
    #     "cid": os.getenv('TO_CID'),
    #     "sec": os.getenv('TO_SEC')
    # }
    client.run(to_auth_dict, ticker='ESU2', interval=5)
