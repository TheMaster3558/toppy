from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional, Union, AsyncIterator, Awaitable

import aiohttp

from .dbl import DBLClient
from .topgg import TopGGClient

if TYPE_CHECKING:
    from .protocols import ClientProtocol
    from .topgg.bot import Bot
    from .topgg.user import User


class Client:
    """A class designed to handle both Top.gg and Discord Bot List
    For individual handling use :class:`DBLClient` or :class:`TopGGClient`

    Parameters
    ----------
    client: :class:`ClientProtocol`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`
        It must fit the :class:`ClientProtocol`
    dbl_token: :class:`str`
        The authorization token for Discord Bot List
    topgg_token: :class:`str`
        The authorization token for Top.gg
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    post_shard_count: :class:`bool`
        Decides whether to post the shard count along with the server count.
        Defaults to False.
    start_on_ready: :class:`bool`:
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`
        Defaults to True
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.
    """
    def __init__(
            self,
            client: ClientProtocol,
            /,
            dbl_token: str,
            topgg_token: str,
            *,
            interval: Optional[float] = None,
            post_shard_count: bool = False,
            start_on_ready: bool,
            session: Optional[aiohttp.ClientSession] = None
    ):
        self.client = client
        session = session or aiohttp.ClientSession()

        self.__dbl: DBLClient = DBLClient(
            client, token=dbl_token,
            interval=interval,
            start_on_ready=start_on_ready,
            session=session
        )

        self.__topgg: TopGGClient = TopGGClient(
            client,
            token=topgg_token,
            interval=interval,
            post_shard_count=post_shard_count,
            start_on_ready=start_on_ready,
            session=session
        )

    @property
    def intervals(self) -> tuple[float, float]:
        """Returns the intervals of the autopost task. First the dbl, then the topgg.
        Returns tuple[:class:`float`]
        """
        return self.__dbl.interval, self.__topgg.interval

    @intervals.setter
    def intervals(self, new: Union[float, tuple[Optional[float], Optional[float]]]) -> None:
        if isinstance(new, (float, int)):
            self.__dbl.interval = new
            self.__topgg.interval = new
        elif isinstance(new, tuple):
            dbl, topgg = new

            if dbl is not None:
                self.__dbl.interval = dbl
            if topgg is not None:
                self.__topgg.interval = topgg

        else:
            raise TypeError(f'Expected `float` or `tuple[float, float]` not {new.__class__.__name__!r}')

    def _merge_starts(self) -> None:
        old = self.client.start

        # used over setup_hook for fork support

        async def start(*args, **kwargs) -> None:
            if self.__dbl.start_on_ready:
                self.__dbl.start()
            if self.__topgg.start_on_ready:
                self.__topgg.start()

            await old(*args, **kwargs)  # type: ignore  # not sure why this happens

        self.client.start = start  # type: ignore # "Cannot assign to method"

    def start(self):
        """Starts the autopost task"""
        self.__dbl.start()
        self.__topgg.start()

    def cancel(self):
        """Cancels the task of auto posting stats"""
        self.__dbl.cancel()
        self.__topgg.cancel()

    @property
    def dbl_task(self) -> asyncio.Task:
        """
        Returns
        --------
        The :class:`asyncio.Task` object for dbl autopost.
        """
        return self.__dbl.task

    @property
    def topgg_task(self) -> asyncio.Task:
        """
        Returns
        --------
        The :class:`asyncio.Task` object for topgg autopost.
        """
        return self.__topgg.task

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List and Top.gg
        All stats are automatically found and posted."""
        await asyncio.gather(self.__dbl.post_stats(), self.__topgg.post_stats())

    async def search_bots(self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
                          ) -> list[Bot]:
        """Search up bots on Top.gg

        Parameters
        ----------
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
        list[:class:`Bot`]:
        """
        return await self.__topgg.search_bots(query=query, limit=limit, offset=offset)

    async def search_one_bot(self, bot_id: int, /) -> Bot:
        """Search a single bot on Top.gg

        Parameters
        ----------
        bot_id: :class:`int`
            The ID to search.
            Positional only.

        Returns
        --------
        :class:`Bot`:
        """
        return await self.search_one_bot(bot_id)

    async def last_1000_votes(self, bot_id: int = None, /) -> AsyncIterator[User]:
        """Get the last 1000 votes of a bot on Top.gg

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
        return self.__topgg.last_1000_votes(bot_id)

    async def check_if_voted(self, bot_id: Optional[int], user_id: int) -> bool:
        """Check if a user has voted on a bot

        Parameters
        ----------
        bot_id: Optional[:class:`int`]
            The ID of the bot.
            Defaults to the Bot initialized with.
        user_id: :class:`int`
            The ID of the user.

        Returns
        --------
        :class:`bool`
        """
        return await self.__topgg.check_if_voted(bot_id, user_id)
