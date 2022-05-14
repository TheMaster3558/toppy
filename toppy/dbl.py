from __future__ import annotations

import asyncio
from typing import Optional, TYPE_CHECKING
from functools import wraps

import aiohttp

from .http import DBLHTTPClient
from . import utils
from .errors import ClientNotReady

if TYPE_CHECKING:
    from .protocols import ClientProtocol


__all__ = (
    'DBLClient',
)


MISSING = utils.MISSING


class DBLClient:
    """A Client to access the Discord Bot List API. This includes auto-posting Discord Bot Stats.

    https://discordbotlist.com/

    Parameters
    ----------
    client: :class:`Client`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`.
    token: :class:`str`
        The token for Discord Bot List.
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    start_on_ready: :class:`bool`
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`.
        Defaults to True.
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.


    .. versionchanged:: 1.4

        Instead of a separate module it is just one file.
    """
    def __init__(
            self,
            client: ClientProtocol,
            /,
            token: str,
            *,
            interval: Optional[float] = None,
            start_on_ready: bool = True,
            session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        self.interval: float = interval or 600

        self.start_on_ready: bool = start_on_ready

        self.client = client
        self.http: DBLHTTPClient = MISSING
        self.token = token
        self.__session: Optional[aiohttp.ClientSession] = session  # protected because may not be real session

        self.__task: asyncio.Task = MISSING
        self._merge()

    @property
    def task(self) -> asyncio.Task:
        """
        The :class:`asyncio.Task` object for autopost.
        """
        return self.__task

    def _merge(self) -> None:
        old_start = self.client.start
        old_close = self.client.close

        # used over setup_hook for fork support
        @wraps(old_start)
        async def start(*args, **kwargs) -> None:
            task = self.client.loop.create_task(old_start(*args, **kwargs))

            self.http = DBLHTTPClient(self.token, session=self.__session)
            if self.start_on_ready:
                self.start()

            await task

        @wraps(old_close)
        async def close() -> None:
            if not self.http.session.closed:
                await self.http.session.close()

            await old_close()

        self.client.start = start  # type: ignore # "Cannot assign to method"
        self.client.close = close  # type: ignore

    def _get_bot_id(self) -> int:
        if self.client.application_id:
            return self.client.application_id
        if self.client.user:
            return self.client.user.id
        raise ClientNotReady()

    def start(self) -> None:
        """Starts the autopost task."""
        self.__task = self.client.loop.create_task(self._post_task(), name='dbl_autopost')

    def cancel(self) -> None:
        """Cancels the task of auto posting stats."""
        self.task.cancel()

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List.
        All stats are automatically found and posted.

        dispatches `dbl_autopost_error` with the argument :class:`aiohttp.ClientResponseError`
        or `dbl_autopost_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'voice_connections': len(self.client.voice_clients),
            'users': len(self.client.users or []),
            'guilds': len(self.client.guilds or [])
        }

        resp = await self.http.post_stats(bot_id, **kwargs)
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            self.client.dispatch('dbl_post_error', exc)
        else:
            self.client.dispatch('dbl_post_success')

    async def _post_task(self) -> None:
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.post_stats()
            await asyncio.sleep(self.interval)
