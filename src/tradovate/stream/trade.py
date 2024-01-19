## Imports
from __future__ import annotations

import logging

from .client import Client
from ..config import CONFIG

## Constants
log = logging.getLogger(__name__)


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
    authorization_dict: dict = {
        "name": CONFIG['TO'].get("to_name"),
        "password": CONFIG['TO'].get('to_password'),
        "appId": CONFIG['TO'].get('to_appid'),
        "appVersion": "1.0",
        "cid": CONFIG['TO'].get('to_cid'),
        "sec": CONFIG['TO'].get('to_sec'),
        "deviceId": CONFIG['TO'].get('to_devid', 1)
    }
    client.run_subcribe(authorization_dict, ticker=ticker, interval=interval)


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
    authorization_dict: dict = {
        "name": CONFIG['TO'].get("to_name"),
        "password": CONFIG['TO'].get('to_password'),
        "appId": CONFIG['TO'].get('to_appid'),
        "appVersion": "1.0",
        "cid": CONFIG['TO'].get('to_cid'),
        "sec": CONFIG['TO'].get('to_sec'),
        "deviceId": CONFIG['TO'].get('to_devid', 1)
    }
    client.run(authorization_dict, ticker='ESU2', interval=5)
