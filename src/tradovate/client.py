## Imports
from __future__ import annotations

import asyncio
from datetime import timedelta

from .accounting import Accounting
from .auth import Profile
from .auth.session import Session
from .stream.utils.typing import CredentialAuthDict
from src.tradovate.config import logger
from ..utils.general import Singleton


## Classes
class Client(Profile, metaclass=Singleton):
    """ Tradovate Client & start of ALL Tradovate async classes inherit from here """

    # -Constructor
    def __init__(self) -> Client:
        # Profile.__init__() # No need to call Super as we're Overriding self.id & self._session
        logger.debug("Starting asynchio Event Loop for Connecting to Tradovate...")
        try:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._session: Session = Session(loop=self._loop)
        self._handle_auto_renewal: asyncio.TimerHandle | None = None

        accounting = Accounting(self._session)
        account = asyncio.run(accounting.account_list())

        self.id = account[0]['id']
        self.name = account[0]['name']

    @property
    def accounting(self) -> Accounting:
        return Accounting(self._session)

    def run(self, event, *args, **kwargs) -> None:
        """Public client loop run method"""
        self._loop.run_until_complete(self._run(event, *args, **kwargs))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            for task in asyncio.all_tasks(loop=self._loop):
                task.cancel()
            self._loop.run_until_complete(self.close())
            self._loop.close()

    async def _run(self, event, *args, **kwargs) -> None:
        self._dispatch(event=event, *args, **kwargs)

    # -Instance Methods: Private
    def _dispatch(self, event: str, *args, **kwargs) -> None:
        """Dispatch task for event name"""
        logger.debug(f"Client event '{event}'")

        method = event
        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._loop.create_task(coro(*args, **kwargs))

    async def _renewal(self) -> None:
        """Task for Session authorization renewal loop"""
        while self._session.authenticated.is_set():
            time = self._session.token_duration - timedelta(minutes=10)
            await asyncio.sleep(time.total_seconds())
            await self._session.renew_access_token()

    # -Instance Methods: Public
    async def authorize(
            self, auth: CredentialAuthDict, auto_renew: bool = True
    ) -> None:
        """Initialize Client authorization and auto-renewal"""
        token_req = await self._session.request_access_token()
        self.id = token_req['accessToken']
        if auto_renew:
            self._loop.create_task(self._renewal(), name="client-renewal")

    async def authorizion_hold(self) -> None:
        """Wait for all authentication setup to be finished"""
        await self._session.authenticated.wait()

    async def close(self) -> None:
        await self._session.close()

    async def process_message(self) -> None:
        """Task for WebSocket loop"""
        print("WebSocket loop>>>>>>>")

    # -Properties: Authenticated
    @property
    def authenticated(self) -> bool:
        return bool(self._session.authenticated.is_set())
