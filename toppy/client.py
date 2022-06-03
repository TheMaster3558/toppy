from __future__ import annotations

import asyncio
import functools
from abc import abstractmethod
from typing import TYPE_CHECKING, AsyncGenerator, ClassVar, Optional, Type

import aiohttp

from .errors import ClientNotReady, HTTPException
from .http import BaseHTTPClient, DiscordBotListHTTPClient, DiscordBotsGGHTTPClient, TopGGHTTPClient
from .utils import copy_doc, MISSING

if TYPE_CHECKING:
    from .protocols import ClientProtocol
    from .models import Bot, User


__all__ = (
    'Client',
    'DiscordBotListClient',
    'DiscordBotsGGClient',
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
        @functools.wraps(old_start)
        async def start(*args, **kwargs) -> None:
            task = self.client.loop.create_task(old_start(*args, **kwargs))

            self.http = self.http_class(self.token, session=self.__session)
            if self.start_on_ready:
                self.start()

            await task

        @functools.wraps(old_close)
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
        try:
            await self.http.post_stats(bot_id, **kwargs)
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


class DiscordBotListClient(BaseClient):
    """A Client to access the Discord Bot List API. This includes auto-posting Discord Bot Stats.

    https://discordbotlist.com/

    Parameters
    ----------
    client: :class:`Client`
        The Discord Bot instance. Any Client derived from `discord.Client` or any other fork's `Client`.
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

    http_class = DiscordBotListHTTPClient
    shortened = 'dbl'

    if TYPE_CHECKING:
        http: DiscordBotListHTTPClient

    async def post_stats(self) -> None:
        """Post your bots stats to Discord Bot List.
        All stats are automatically found and posted.

        dispatches `dbl_post_error` with the argument :class:`toppy.HTTPException` or derived classes
        or `dbl_post_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'voice_connections': len(self.client.voice_clients),
            'users': len(self.client.users or []),
            'guilds': len(self.client.guilds or [])
        }

        await self._post_stats_handler(bot_id, **kwargs)


class DiscordBotsGGClient(BaseClient):
    """A Client to access the DiscordBotsGG. This includes auto-posting Discord Bot Stats.

    https://discord.bots.gg/

    Parameters
    ----------
    client: :class:`Client`
        The Discord Bot instance. Any Client derived from `discord.Client` or any other fork's `Client`.
    token: :class:`str`
        The token for DiscordBotsGG.
    interval: Optional[:class:`float`]
        The interval in seconds to auto-post the stats.
        Defaults to 600.
    start_on_ready: :class:`bool`
        Whether to start the auto post task when the bot is ready.
        If False then it must be manually started with `start`.
        Defaults to True.
    session: Optional[:class:`aiohttp.ClientSession`]
        The session for the HTTP Client.


    .. versionadded:: 1.6
    """

    http_class = DiscordBotsGGHTTPClient
    shortened = 'dbgg'

    if TYPE_CHECKING:
        http: DiscordBotsGGHTTPClient

    async def post_stats(self) -> None:
        """Post your bots stats to DiscordBotsGG
        All stats are automatically found and posted.

        dispatches `dbgg_post_error` with the argument :class:`toppy.HTTPException` or derived classes
        or `dbgg_post_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
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
        The Discord Bot instance. Any Client derived from `discord.Client` or any other fork's `Client`.
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
        
        Example
        ----------
        .. code:: py

            async for user in topgg.last_1000_votes():
                ...
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

        dispatches `topgg_post_error` with the argument :class:`toppy.HTTPException` or derived classes
        or `topgg_post_success` with no arguments.
        """

        bot_id = self._get_bot_id()

        kwargs = {
            'server_count': len(self.client.guilds or [])
        }

        if self.post_shard_count:
            kwargs['shard_count'] = self.client.shard_count or 1

        await self._post_stats_handler(bot_id, **kwargs)


class Client:
    """A class designed to handle Discord Bot List, DiscordBotsGG, and/or Top.gg

    Parameters
    ----------
    client: :class:`ClientProtocol`
        The Discord Bot instance. Any Client derived from `discord.Client` or any other fork's `Client`.
        It must fit the :class:`ClientProtocol`.
    dbl_token: :class:`str`
        The authorization token for Discord Bot List.
    dbgg_token: :class:`str`
        The authentication token for DiscordBotsGG
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

    .. versionchanged:: 1.6
        Add support for DiscordBotsGG
    """
    clients: ClassVar[tuple] = (
        ('dbl', DiscordBotListClient),
        ('dbgg', DiscordBotsGGClient),
        ('topgg', TopGGClient)
    )

    def __init__(
            self,
            client: ClientProtocol,
            **options
    ):
        self.client = client

        self._original_options = options
        self.__session: aiohttp.ClientSession = MISSING

        self.__dbl: Optional[DiscordBotListClient] = None
        self.__dbgg: Optional[DiscordBotsGGClient] = None
        self.__topgg: Optional[TopGGClient] = None

    def _init(self):
        interval: int = self._original_options.get('interval', 600)
        start_on_ready: bool = self._original_options.get('start_on_ready', True)

        for name, cls in self.clients:
            token = self._original_options.get(f'{name}_token')

            if not token:
                continue

            kwargs = {
                'interval': interval,
                'start_on_ready': start_on_ready,
                'session': self.__session
            }

            if 'post_shard_count' in cls.__init__.__annotations__:
                kwargs['post_shard_count'] = kwargs.get('post_shard_count', False)

            client = cls(self.client, token, **kwargs)
            setattr(self, f'__{name}', client)

    def _merge(self) -> None:
        old_start = self.client.start
        old_close = self.client.close

        # used over setup_hook for fork support
        @functools.wraps(old_start)
        async def start(*args, **kwargs) -> None:
            self.__session = aiohttp.ClientSession(loop=self.client.loop)
            await old_start(*args, **kwargs)

        @functools.wraps(old_close)
        async def close() -> None:
            await self.__session.close()
            await old_close()

        self.client.start = start  # type: ignore # "Cannot assign to method"
        self.client.close = close  # type: ignore

    def _get_clients(self) -> list[BaseClient]:
        clients = []

        for client, _ in self.clients:
            instance = getattr(self, client)
            if instance:
                clients.append(instance)

        return clients

    @copy_doc(BaseClient.start)
    def start(self):
        for client in self._get_clients():
            client.start()

    @copy_doc(BaseClient.cancel)
    def cancel(self):
        """Cancels the task of auto posting stats."""
        for client in self._get_clients():
            client.cancel()

    @property
    def dbl(self) -> Optional[DiscordBotListClient]:
        """
        Access the Client for Discord Bot List.
        
        Returns
        --------
        Optional[:class:`DBLCLient`]
        """
        return self.__dbl

    @property
    def dbgg(self) -> Optional[DiscordBotsGGClient]:
        """
        Access the Client for DiscordBotsGG.

        Returns
        --------
        Optional[:class:`DiscordBotsGGClient`]
        """
        return self.__dbgg

    @property
    def topgg(self) -> Optional[TopGGClient]:
        """
        Access the Client for Top.gg.
        
        Returns
        --------
        Optional[:class:`TopGGClient`]
        """
        return self.__topgg

    async def post_stats(self) -> None:
        """Post your bots stats to all websites with a token found.
        All stats are automatically found and posted."""
        tasks = [
            self.client.loop.create_task(client.post_stats())
            for client in self._get_clients()
        ]

        await asyncio.gather(*tasks)
