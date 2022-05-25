from __future__ import annotations

import asyncio
from abc import abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, AsyncGenerator, Optional, Type, Union

import aiohttp

from .errors import ClientNotReady, HTTPException
from .http import BaseHTTPClient, DBLHTTPClient, TopGGHTTPClient
from .utils import MISSING

if TYPE_CHECKING:
    from .protocols import ClientProtocol
    from .models import Bot, User


__all__ = (
    'Client',
    'DBLClient',
    'TopGGClient'
)


class BaseClient:
    http_class: Type[BaseHTTPClient]
    shortened: str

    def __init__(
            self,
            client: ClientProtocol,
            token: str,
            *,
            interval: Optional[float] = None,
            start_on_ready: bool = True,
            session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        self.interval: float = interval or 600

        self.start_on_ready: bool = start_on_ready

        self.client = client
        self.http: BaseHTTPClient = MISSING
        self.token = token
        self.__session: Optional[aiohttp.ClientSession] = session

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

            self.http = self.http_class(self.token, session=self.__session)
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
        self.__task = self.client.loop.create_task(
            self._post_task(),
            name=f'{self.shortened}_autopost'
        )

    def cancel(self) -> None:
        """Cancels the task of auto posting stats."""
        self.task.cancel()

    async def _post_stats_handler(self, bot_id: int, **kwargs) -> None:
        resp = await self.http.post_stats(bot_id, **kwargs)
        try:
            resp.raise_for_status()
        except HTTPException as exc:
            self.client.dispatch(f'{self.shortened}_post_error', exc)
        else:
            self.client.dispatch(f'{self.shortened}_post_success')

    async def _post_task(self) -> None:
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.post_stats()
            await asyncio.sleep(self.interval)

    @abstractmethod
    async def post_stats(self) -> None:
        raise NotImplementedError


class DBLClient(BaseClient):
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

    .. versionchanged:: 1.5
        Moved to toppy.client
    """

    http_class = DBLHTTPClient
    shortened = 'dbl'

    if TYPE_CHECKING:
        http: DBLHTTPClient

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List.
        All stats are automatically found and posted.

        dispatches `dbl_autopost_error` with the argument :class:`toppy.HTTPException` or derived classes
        or `dbl_autopost_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'voice_connections': len(self.client.voice_clients),
            'users': len(self.client.users or []),
            'guilds': len(self.client.guilds or [])
        }

        await self._post_stats_handler(bot_id, **kwargs)


class TopGGClient(BaseClient):
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


    .. versionchanged:: 1.4

        Instead of a separate module it is just one file.

    .. versionchanged:: 1.5
        Moved to toppy.client
    """

    http_class = TopGGHTTPClient
    shortened = 'topgg'

    if TYPE_CHECKING:
        http: TopGGHTTPClient

    def __init__(self, *args, post_shard_count: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_shard_count = post_shard_count

    async def search_bots(self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
                          ) -> list[Bot]:
        """Search up bots on Top.gg.

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
        """Search a single bot on Top.gg.

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

    async def last_1000_votes(self, bot_id: int = None, /) -> AsyncGenerator[User, None]:
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
        bot_id: Optional[:class:`int`]
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

        dispatches `topgg_autopost_error` with the argument :class:`toppy.HTTPException` or derived classes
        or `topgg_autopost_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'server_count': len(self.client.guilds or [])
        }

        if self.post_shard_count:
            kwargs['shard_count'] = self.client.shard_count or 1

        await self._post_stats_handler(bot_id, **kwargs)


class Client:
    """A class designed to handle both Top.gg and Discord Bot List.
    For individual handling use :class:`DBLClient` or :class:`TopGGClient`

    Parameters
    ----------
    client: :class:`ClientProtocol`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`.
        It must fit the :class:`ClientProtocol`.
    dbl_token: :class:`str`
        The authorization token for Discord Bot List.
    topgg_token: :class:`str`
        The authorization token for Top.gg.
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    post_shard_count: :class:`bool`
        Decides whether to post the shard count along with the server count.
        Defaults to False.
    start_on_ready: :class:`bool`
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`.
        Defaults to True.
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.

    .. versionchanged:: 1.5
        ``client`` is no longer positional only.
    """
    def __init__(
            self,
            client: ClientProtocol,
            **options
    ):
        self.client = client

        self._original_options = options

        self.__dbl: DBLClient = MISSING
        self.__topgg: TopGGClient = MISSING

    @property
    def intervals(self) -> tuple[float, float]:
        """Returns the intervals of the autopost task. First the dbl, then the topgg.

        Returns
        --------
        tuple[:class:`float`]
        """
        return self.__dbl.interval, self.__topgg.interval

    @intervals.setter
    def intervals(self, new: Union[float, tuple[Optional[float], Optional[float]]]) -> None:
        """Set new intervals.
         If you pass in :class:`float` both the dbl and topgg client's interval will be set to it.
         If you pass in tuple[Optional[:class:`float`, Optional[:class:`float`]] then the first
         will set the dbl client and the second will set the topgg client.

         Raises
         -------
         :exc:`TypeError` If it didn't receive :class:`float`, :class:`int`, or :class:`tuple`
         """
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
        old_start = self.client.start
        old_close = self.client.close

        # used over setup_hook for fork support
        @wraps(old_start)
        async def start(*args, **kwargs) -> None:
            task = self.client.loop.create_task(old_start(*args, **kwargs))

            session = self._original_options.get('session', aiohttp.ClientSession(loop=self.client.loop))

            self.__dbl = DBLClient(
                self.client, token=self._original_options['dbl_token'],
                interval=self._original_options.get('interval'),
                start_on_ready=self._original_options.get('start_on_ready', True),
                session=session
            )

            self.__topgg = TopGGClient(
                self.client, token=self._original_options['topgg_token'],
                interval=self._original_options.get('interval'),
                post_shard_count=self._original_options.get('post_shard_count', False),
                start_on_ready=self._original_options.get('start_on_ready', True),
                session=session
            )

            if self._original_options.get('start_on_ready', True):
                self.__dbl.start()
                self.__topgg.start()

            await task

        @wraps(old_close)
        async def close() -> None:
            if not self.__dbl.http.session.closed:
                await self.__dbl.http.session.close()
            if not self.__topgg.http.session.closed:
                await self.__topgg.http.session.close()

            await old_close()

        self.client.start = start  # type: ignore # "Cannot assign to method"
        self.client.close = close  # type: ignore

    def start(self):
        """Starts the autopost task."""
        self.__dbl.start()
        self.__topgg.start()

    def cancel(self):
        """Cancels the task of auto posting stats."""
        self.__dbl.cancel()
        self.__topgg.cancel()

    @property
    def dbl_task(self) -> asyncio.Task:
        """
        The :class:`asyncio.Task` object for dbl autopost.
        """
        return self.__dbl.task

    @property
    def topgg_task(self) -> asyncio.Task:
        """
        The :class:`asyncio.Task` object for topgg autopost.
        """
        return self.__topgg.task

    @property
    def dbl(self) -> DBLClient:
        """
        Access the interval Client for Discord Bot List.
        
        Returns
        --------
        :class:`DBLCLient`
        """
        return self.__dbl

    @property
    def topgg(self) -> TopGGClient:
        """
        Access the interval Client for Top.gg.
        
        Returns
        --------
        :class:`TopGGClient`
        """
        return self.__topgg

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List and Top.gg.
        All stats are automatically found and posted."""
        await asyncio.gather(self.__dbl.post_stats(), self.__topgg.post_stats())

    async def search_bots(self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
                          ) -> list[Bot]:
        """Search up bots on Top.gg.

        Parameters
        -----------
        query: :class:`str`
            The query to use when searching.
        limit: Optional[:class:`int`]
            The limit of :class:`Bot`'s to return.
            Keyword only.
        offset: Optional[:class:`int`]
            The amount of bots to skip in the results.
            Keyword only.

        Returns
        --------
        list[:class:`Bot`]
        """
        return await self.__topgg.search_bots(query=query, limit=limit, offset=offset)

    async def search_one_bot(self, bot_id: int, /) -> Bot:
        """Search a single bot on Top.gg.

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

    async def last_1000_votes(self, bot_id: int = None, /) -> AsyncGenerator[User, None]:
        """Get the last 1000 votes of a bot on Top.gg

        Parameters
        -----------
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
