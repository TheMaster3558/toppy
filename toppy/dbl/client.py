from __future__ import annotations

import asyncio
from typing import Optional, TYPE_CHECKING

import aiohttp

from .http import DBLHTTPClient
from .. import utils
from ..errors import ClientNotReady

if TYPE_CHECKING:
    from ..protocols import Client


MISSING = utils.MISSING


class DBLClient:
    """A Client to access the Discord Bot List API. This includes auto-posting Discord Bot Stats.

    https://discordbotlist.com/

    Parameters
    ----------
    client: :class:`Client`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`
    token: :class:`str`
        The token for Discord Bot List
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    start_on_ready: :class:`bool`:
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`
        Defaults to True
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.

    Attributes
    ----------
    interval: :class:`float`
        The interval in seconds to auto-post the stats.
    """
    def __init__(
            self,
            client: Client,
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
        self.http: DBLHTTPClient = DBLHTTPClient(token, loop=self.client.loop, session=session)

        self.__task: asyncio.Task = MISSING
        self._merge_starts()

    @property
    def task(self) -> asyncio.Task:
        """
        Returns
        --------
        The :class:`asyncio.Task` object for autopost.
        """
        return self.__task

    def _merge_starts(self) -> None:
        old = self.client.start

        # used over setup_hook for fork support

        async def start(*args, **kwargs) -> None:
            if self.start_on_ready:
                self.start()

            await old(*args, **kwargs)

        self.client.start = start  # type: ignore # "Cannot assign to method"

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
        """Cancels the task of auto posting stats"""
        self.task.cancel()

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List
        All stats are automatically found and posted

        dispatches `dbl_autopost_error` with the argument :class:`aiohttp.ClientResponseError`
        or `dbl_autopost_success` with no arguments
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
            self.client.dispatch('dbl_autopost_error', exc)
        else:
            self.client.dispatch('dbl_autopost_success')

    async def _post_task(self) -> None:
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.post_stats()
            await asyncio.sleep(self.interval)
