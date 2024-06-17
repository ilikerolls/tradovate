from __future__ import annotations

import asyncio
import json

import pytz
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone

from aiohttp import ClientSession, ClientResponse

from ..stream.utils import urls, timestamp_to_datetime
from ..stream.utils.errors import (
    LoginInvalidException, LoginCaptchaException
)
from src.config import CONFIG_ACTIONS, redis_client, logger, to_auth_dict
from ...utils.general import parse_a_date


class Session:

    # -Constructor
    def __init__(self, *, loop: AbstractEventLoop | None = None) -> Session:
        """ Authenticates with Tradovate & Holds Session Data """
        self.authenticated: asyncio.Event = asyncio.Event()
        self.token_expiration: datetime | None = None
        self._session: ClientSession | None = None
        self._loop: AbstractEventLoop = loop or asyncio.get_event_loop()
        self._loop.create_task(self.__ainit__(), name="session-client")

        self.URL: str = urls.http_base_live if CONFIG_ACTIONS['tradovate']['TO'].get('to_env').upper() == 'LIVE' else urls.http_base_demo
        tokens = redis_client.get('TO_TOKEN')
        if tokens is not None:
            tokens = json.loads(tokens)
            age_secs = self._get_age_secs(tokens)

            print("*******************", age_secs)
            if age_secs < 120 and age_secs > 60:
                tokens = asyncio.run(self.renew_access_token(tokens['accessToken']))
            elif age_secs < 60:
                print(">>>>>>>>>>>>>request_access_token 1:")
                tokens = asyncio.run(self.request_access_token())
        else:
            print(">>>>>>>>>>>>>request_access_token 2")
            tokens = asyncio.run(self.request_access_token())

        print(">>>>>>>>>>>>>.", tokens)
        self.access_tokens: dict = tokens
        self.access_token: str = self.access_tokens['accessToken']
        self.market_data_access_token: str = self.access_tokens['mdAccessToken']
        # self.token_expiration_time: str = self.access_tokens['expirationTime'].replace("T", " ")[:-8]
        self.headers: dict = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # -Dunder Methods
    async def __ainit__(self) -> None:
        self._session = ClientSession(loop=self._loop, raise_for_status=True)

    def __repr__(self) -> str:
        str_ = f"Session(authenticated={self.authenticated.is_set()}"
        if self.authenticated.is_set():
            str_ += f", duration={self.token_duration}"
        return f"{str_})"

    async def __aenter__(self):
        """Enter client session."""
        self._session = ClientSession()
        return self

    async def __aexit__(self):
        """Exit client session."""
        await self._session.close()

    async def close(self) -> None:
        await self._session.close()
        self.authenticated.clear()

    async def request_access_token(self) -> dict[str, str]:
        """
        Request Session authorization Returns Dict of
        https://api.tradovate.com/#tag/Authentication/operation/oAuthToken
        """
        await self.__aenter__()

        logger.debug("Session event 'request'")

        res = await self._session.post(urls.http_auth_request, json=to_auth_dict, ssl=False)

        return await self._update_authorization(res)

    async def renew_access_token(self, accessToken: str) -> dict[str, str]:
        """
        Renew Session authorization
        :param accessToken: Access Token to Log into Trdovate
        """
        await self.__aenter__()

        self.headers: dict = {
            'Authorization': f'Bearer {accessToken}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        logger.debug("Session event 'renew'")
        res = await self._session.post(urls.http_auth_renew)
        return await self._update_authorization(res)

    # -Instance Methods: Private
    async def _update_authorization(
            self, res: ClientResponse
    ) -> dict[str, str]:
        """
        Updates Session authorization fields
        https://api.tradovate.com/#tag/Authentication/operation/oAuthToken
        """
        res_dict = await res.json()

        # print(">>>>>>>>>>>+++++", res_dict)

        # -Invalid Credentials
        if 'errorText' in res_dict and len(res_dict['errorText']) > 0:
            self.authenticated.clear()
            raise LoginInvalidException(res_dict['errorText'])
        # -Captcha Limiting
        if 'p-ticket' in res_dict:
            self.authenticated.clear()
            raise LoginCaptchaException(
                res_dict['p-ticket'], int(res_dict['p-time']),
                bool(res_dict['p-captcha'])
            )
        # -Access Token
        logger.debug("Session event 'authorized'")
        self.authenticated.set()

        await redis_client.set('TO_TOKEN', json.dumps(res_dict))

        self.token_expiration = timestamp_to_datetime(res_dict['expirationTime'])

        return res_dict

    def _get_age_secs(self, tokens):
        if not tokens:
            return -1
        expiration_time = tokens["expirationTime"]
        dt = int(datetime.now(tz=pytz.UTC).strftime("%s"))
        t = parse_a_date(expiration_time)
        dt2 = int(t.strftime("%s"))
        age_secs = dt2 - dt
        print("******************************************************age_secs:", age_secs)
        return age_secs

    async def get(self, url: str) -> dict:
        """Send GET request to a spicified url."""
        await self.__aenter__()
        url = f"{self.URL + url}"

        async with self._session.get(url, headers=self.headers, ssl=False) as resp:
            data = await resp.read()
            return json.loads(data) if data else {}

    async def post(self, url: str, payload: dict):
        """Send POST request to a specified url with a specified payload."""
        await self.__aenter__()
        url = f"{self.URL + url}"
        print("url:", url)
        async with self._session.post(url, headers=self.headers, json=payload) as resp:
            data = await resp.read()
            return json.loads(data) if data else {}

    # -Property
    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def token_duration(self) -> timedelta:
        return self.token_expiration - datetime.now(timezone.utc)

    @property
    def token_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.token_expiration
