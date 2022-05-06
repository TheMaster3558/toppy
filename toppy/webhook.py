from __future__ import annotations

from typing import Literal, Optional, TYPE_CHECKING, Type, cast
import asyncio
from json.decoder import JSONDecodeError

from aiohttp import web

if TYPE_CHECKING:
    from .protocols import ClientProtocol, Snowflake


class DiscordBotListPayload:
    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data

        self.__user: Optional[Snowflake] = None

    @property
    def raw(self) -> dict:
        """
        Returns the raw data sent.

        Returns
        --------
        :class:`dict`
        """

        return self.__data

    @property
    def admin(self) -> bool:
        """
        If the user is a site administrator for Discord Bot List.

        Returns
        --------
        :class:`bool`
        """

        return self.__data['admin']

    @property
    def avatar(self) -> str:
        """
        The avatar hash of the user.

        Returns
        --------
        :class:`str`
        """

        return self.__data['admin']

    @property
    def username(self) -> str:
        """
        The username of the user who voted.

        Returns
        --------
        :class:`str`
        """

        return self.__data['username']

    @property
    def user_id(self) -> int:
        """
        The ID of the user who voted.

        Returns
        --------
        :class:`int`
        """

        return int(self.__data['id'])

    @property
    def user(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the user based on what library your client is from.
        If missing use ``fetch()``

        Returns
        --------
        Optional[:class:`Snowflake`]
        """

        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure ``user`` is not :class:`None`
        """

        self.__user = await self.__client.fetch_user(self.user_id)


class TopGGVotePayload:
    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data

        self.__bot_id: int = data['bot']
        self.__user_id: int = data['user']

        self.__bot: Optional[Snowflake] = None
        self.__user: Optional[Snowflake] = None

    @property
    def raw(self) -> dict:
        """
        Returns the raw data sent.

        Returns
        --------
        :class:`dict`
        """

        return self.__data

    @property
    def bot_id(self) -> int:
        """
        Discord ID of the bot that received a vote.

        Returns
        --------
        :class:`int`
        """

        return self.__bot_id

    @property
    def user_id(self) -> int:
        """
        Discord ID of the user who voted.

        Returns
        --------
        :class:`int`
        """
        return self.__user_id

    @property
    def type(self) -> Literal["upvote", "test"]:
        """
        The type of the vote (should always be "upvote" except when using the test button it's "test").

        Returns
        --------
        Literal["upvote", "test"]
        """

        return self.__data['type']

    @property
    def is_weekend(self) -> bool:
        """
        Whether the weekend multiplier is in effect, meaning users votes count as two.

        Returns
        --------
        :class:`bool`
        """

        return self.__data['isWeekend']

    @property
    def query(self) -> Optional[str]:
        """
        Query string params found on the /bot/:ID/vote page. Example: ?a=1&b=2.

        Returns
        --------
        :class:`str`
        """

        return self.__data.get('query')

    @property
    def bot(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the bot voted for based on what library your client is from.
        If missing use ``fetch()``

        Returns
        --------
        Optional[:class:`user`]
        """

        return self.__bot or self.__client.get_user(self.bot_id)

    @property
    def user(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the user based on what library your client is from.
        If missing use ``fetch()``

        Returns
        --------
        Optional[:class:`Snowflake`]
        """

        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure ``user`` and ``bot`` are not :class:`None`
        """

        self.__bot = await self.__client.fetch_user(self.bot_id)
        self.__user = await self.__client.fetch_user(self.user_id)


class CallableClassMethod(classmethod):
    async def __call__(self, *args, **kwargs):
        return await self.__func__(WebhookServer, *args, **kwargs)


class CopyClassMeta(type):
    # class must be deep copied
    # aiohttp doesn't support self so class methods must be used
    # in result we must use this to make the class work as an instance
    def __call__(cls, *args, **kwargs) -> WebhookServer:
        webhook_server_copy = type(
            'WebhookServer', WebhookServer.__bases__, dict(WebhookServer.__dict__)
        )
        return webhook_server_copy(*args, **kwargs)


class WebhookServer(web.Application):
    """
    A webhooks server to receives votes and dispatch them to your bot!

    Parameters
    -----------
    client: :class:`ClientProtocol`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`
        It must fit the :class:`ClientProtocol`
    dbl_auth: Optional[:class:`str`]
        The Discord Bot List webhook secret
    topgg_auth: Optional[:class:`str`]
        The Authorization for the webhook
    **kwargs:
        Keyword arguments to pass onto the super call for :class:`aiohttp.web.Application`
    """

    _routes = web.RouteTableDef()

    client: ClientProtocol
    dbl_auth: Optional[str]
    topgg_auth: Optional[str]

    def __init__(self, client: ClientProtocol, dbl_auth: Optional[str] = None,
                 topgg_auth: Optional[str] = None, **kwargs):
        cls = self.__class__
        cls.client = client
        cls.dbl_auth = dbl_auth
        cls.topgg_auth = topgg_auth

        super().__init__(**kwargs)
        self.add_routes(self._routes)

    @_routes.post('/dbl')
    @CallableClassMethod
    async def dbl_votes(cls, request: web.Request) -> web.Response:
        if TYPE_CHECKING:
            cast(Type[WebhookServer], cls)

        if cls.dbl_auth:
            if request.headers.get('Authorization') != cls.dbl_auth:
                return web.Response(status=401)

        try:
            data = await request.json()
        except JSONDecodeError:
            return web.Response(status=400)

        payload = TopGGVotePayload(cls.client, data)
        cls.client.dispatch('dbl_vote', payload)

        return web.Response(status=200, body=__package__)

    @_routes.get('/topgg')
    @CallableClassMethod
    async def top_gg_votes(cls, request: web.Request) -> web.Response:
        if TYPE_CHECKING:
            cast(Type[WebhookServer], cls)

        if cls.topgg_auth:
            if request.headers.get('Authorization') != cls.topgg_auth:
                return web.Response(status=401)

        try:
            data = await request.json()
        except JSONDecodeError:
            return web.Response(status=400)

        payload = TopGGVotePayload(cls.client, data)
        cls.client.dispatch('topgg_vote', payload)

        return web.Response(status=200, body=__package__)

    def run(self, **kwargs) -> asyncio.Task:
        """
        Run the application in the background.

        Parameters
        -----------
        **kwargs: The kwargs to pass into `aiohttp.web.TCPSite
        <https://docs.aiohttp.org/en/stable/web_reference.html?highlight=TCPSite>`__

        Returns
        --------
        :class:`asyncio.Task`
        """

        async def runner_task():
            runner = web.AppRunner(self)
            await runner.setup()

            site = web.TCPSite(runner, **kwargs)
            await site.start()

        loop = self.client.loop
        return loop.create_task(runner_task())
