from __future__ import annotations

from typing import Literal, Optional, TYPE_CHECKING, Type, Union, ClassVar
import logging
import os
from datetime import datetime
from json.decoder import JSONDecodeError

from aiohttp import web

from .utils import MISSING

if TYPE_CHECKING:
    from .protocols import ClientProtocol, Snowflake


__all__ = (
    'create_webhook_server',
    'DiscordBotListVotePayload',
    'TopGGVotePayload'
)


_log = logging.getLogger(__name__)


# the following documentation has been pulled from the Discord Bot List and Top.gg documentation
class DiscordBotListVotePayload:
    """
    A class to represent the a Discord Bot List webhook payload

    .. versionadded:: 1.3
    """

    SITE: ClassVar[str] = 'Discord Bot List'

    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data
        self.__time = datetime.now()

        self.__user: Optional[Snowflake] = None

    @property
    def time(self) -> datetime:
        return self.__time

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
        Returns the :class:`User` object for the user based on what library your client is from.
        If missing use :func:`DiscordBotListVotePayload.fetch()`.

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure `user` is not ``None``.
        """
        self.__user = await self.__client.fetch_user(self.user_id)


class TopGGVotePayload:
    """
    A class to represent the a Top.gg webhook payload

    .. versionadded:: 1.3
    """

    SITE: ClassVar[str] = 'Top.gg'

    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data
        self.__time = datetime.now()

        self.__bot_id: int = data['bot']
        self.__user_id: int = data['user']

        self.__bot: Optional[Snowflake] = None
        self.__user: Optional[Snowflake] = None

    @property
    def time(self) -> datetime:
        return self.__time

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
        If missing use :func:`TopGGVotePayload.fetch()`

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__bot or self.__client.get_user(self.bot_id)

    @property
    def user(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the user based on what library your client is from.
        If missing use :func:`TopGGVotePayload.fetch()`

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure `TopGGVotePayload.user` and `TopGGVotePayload.bot`
        are not ``None``.
        """
        self.__bot = await self.__client.fetch_user(self.bot_id)
        self.__user = await self.__client.fetch_user(self.user_id)


def create_webhook_server(
        client: ClientProtocol,
        *,
        dbl_auth: Optional[str] = MISSING,
        topgg_auth: Optional[str] = MISSING,
        web_app_class: Type[web.Application] = web.Application,
        application: Optional[web.Application] = None,
        **kwargs
) -> web.Application:
    """
    A webhooks server to receives votes and dispatch them to your bot!
    Go to your bot's edit page on Discord Bot List or Top.gg do add the link and authorization.

    Parameters
    -----------
    client: :class:`ClientProtocol`
        The Discord Bot instance. Any Client derived from :class:`discord.Client` or any other fork's `Client`.
        It must fit the :class:`ClientProtocol`.
    dbl_auth: Optional[:class:`str`]
        The Discord Bot List webhook secret. This can be made in the bot's edit section.
    topgg_auth: Optional[:class:`str`]
        The Authorization for the webhook. You can make this in the webhooks section of the bot's edit section.
    web_app_class: Type[:class:`aiohttp.web.Application`]
        The web application class to use. Must be derived from :class:`aiohttp.web.Application`.
        If combined with `application` this will be ignored.
    application: :class:`aiohttp.web.Application`
        A pre-existing application to use.
    **kwargs:
        Keyword arguments to pass onto `web_app_class`.

    Returns
    --------
    The class from `web_app_class` with the routes added.
    The routes are posts to ``/dbl`` and/or ``/topgg``.

    .. versionadded:: 1.3
    """
    if dbl_auth is MISSING:
        dbl_auth = os.urandom(16).hex()
    if topgg_auth is MISSING:
        topgg_auth = os.urandom(16).hex()

    routes = web.RouteTableDef()

    @routes.post('/dbl')
    async def dbl_votes(request: web.Request) -> web.Response:
        if dbl_auth is not None:
            if request.headers.get('Authorization') != dbl_auth:
                return web.Response(status=401)

        try:
            data = await request.json()
        except JSONDecodeError:
            return web.Response(status=400)

        payload = TopGGVotePayload(client, data)
        client.dispatch('dbl_vote', payload)

        return web.Response(status=200, body=__package__)

    @routes.post('/dbl')
    async def topgg_votes(request: web.Request) -> web.Response:
        if topgg_auth is not None:
            if request.headers.get('Authorization') != topgg_auth:
                return web.Response(status=401)

        try:
            data = await request.json()
        except JSONDecodeError:
            return web.Response(status=400)

        payload = TopGGVotePayload(client, data)
        client.dispatch('topgg_vote', payload)

        return web.Response(status=200, body=__package__)

    if not application:
        app = web_app_class(**kwargs)
    else:
        app = application

    app.add_routes(routes)

    return app
