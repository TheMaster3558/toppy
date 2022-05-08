from __future__ import annotations

import asyncio
from typing import Optional, AsyncIterator, TYPE_CHECKING
from functools import wraps

import aiohttp

from .http import TopGGHTTPClient
from .bot import Bot
from .user import User
from .. import utils
from ..errors import ClientNotReady

if TYPE_CHECKING:
    from ..protocols import ClientProtocol


__all__ = (
    'TopGGClient'
)

MISSING = utils.MISSING


class TopGGClient:
    """A Client to access the Top.gg API. This includes auto-posting Discord Bot Stats
    and accessing data about other Discord Bots on Top.gg.

    https://top.gg/

    Parameters
    ----------
    client: :class:`Client`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`.
    token: :class:`str`
        The token found in the Webhooks tab of the bots owner only section.
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    post_shard_count: :class:`bool`
        Decides whether to post the shard count along with the server count.
        Defaults to False.
    start_on_ready: :class:`bool`:
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`.
        Defaults to True.
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.

    Attributes
    ----------
    interval: :class:`float`
        The interval in seconds to auto-post the stats.
    """

    def __init__(
            self,
            client: ClientProtocol,
            /,
            token: str,
            *,
            interval: Optional[float] = None,
            post_shard_count: bool = False,
            start_on_ready: bool = True,
            session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        self.interval: float = interval or 600

        self.post_shard_count: bool = post_shard_count
        self.start_on_ready: bool = start_on_ready

        self.client = client
        self.http: TopGGHTTPClient = MISSING
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

            self.http = TopGGHTTPClient(self.token, session=self.__session)
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
        self.__task = self.client.loop.create_task(self._post_task(), name='topgg_autopost')

    def cancel(self) -> None:
        """Cancels the task of auto posting stats."""
        self.task.cancel()

    async def search_bots(self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
                          ) -> list[Bot]:
        """Search up bots on Top.gg

        Parameters
        -----------
        query: :class:`str`
            The query to use when searching.
        limit: Optional[:class:`int`]
            The limit of :class:`Bot` to return.
            Keyword only.
        offset: Optional[:class:`int`]
            The amount of bots to skip in the results.
            Keyword only.

        Returns
        --------
        list[:class:`Bot`]
        """
        raw_bots = await self.http.search_bots(query, limit=limit, offset=offset)
        return [Bot(bot) for bot in raw_bots]

    async def search_one_bot(self, bot_id: int, /) -> Bot:
        """Search a single bot on Top.gg

        Parameters
        ----------
        bot_id: :class:`int`
            The ID to search.
            Positional only.

        Returns
        --------
        :class:`Bot`
        """
        data = await self.http.search_one_bot(bot_id)
        return Bot(data)

    async def last_1000_votes(self, bot_id: int = None, /) -> AsyncIterator[User]:
        """Get the last 1000 votes of a bot on Top.gg.

        Parameters
        ----------
        bot_id: Optional[:class:`int`]
            The ID of the bot.
            Defaults to the Bot initialized with.
            Positional only.

        Yields
        -------
        :class:`User`
        """
        bot_id = bot_id or self._get_bot_id()

        users = await self.http.last_1000_votes(bot_id)
        for user in users:
            yield User(user)

    async def check_if_voted(self, bot_id: Optional[int], user_id: int) -> bool:
        """Check if a user has voted on a bot.

        Parameters
        ----------
        bot_id: Optional:class:`int`
            The ID of the bot.
            Defaults to the Bot initialized with.
        user_id: :class:`int`
            The ID of the user.

        Returns
        --------
        :class:`bool`
        """
        bot_id = bot_id or self._get_bot_id()

        return await self.http.user_vote(bot_id, user_id)

    async def post_stats(self) -> None:
        """Post your bots stats to Top.gg.
        All stats are automatically found and posted.

        dispatches `topgg_autopost_error` with the argument :class:`aiohttp.ClientResponseError`
        or `topgg_autopost_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'server_count': len(self.client.guilds or [])
        }

        if self.post_shard_count:
            kwargs['shard_count'] = self.client.shard_count or 1

        resp = await self.http.post_stats(bot_id, **kwargs)
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            self.client.dispatch('topgg_post_error', exc)
        else:
            self.client.dispatch('topgg_post_success')

    async def _post_task(self) -> None:
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.post_stats()
            await asyncio.sleep(self.interval)
