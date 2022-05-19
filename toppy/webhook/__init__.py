from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Type, Union
import logging
import os
from json.decoder import JSONDecodeError

from aiohttp import web

from .payload import DiscordBotListVotePayload, TopGGVotePayload
from .cache import SQLDatabase, CachedVote, reset
from ..utils import MISSING

if TYPE_CHECKING:
    from os import PathLike
    from ..protocols import ClientProtocol


__all__ = (
    'create_webhook_server',
    # payloads
    'DiscordBotListVotePayload',
    'TopGGVotePayload',
    # databases
    'SQLDatabase',
    'CachedVote'
)


_log = logging.getLogger(__name__)


def create_webhook_server(
        client: ClientProtocol,
        *,
        dbl_auth: Optional[str] = MISSING,
        topgg_auth: Optional[str] = MISSING,
        web_app_class: Type[web.Application] = web.Application,
        application: Optional[web.Application] = None,
        cache: bool = False,
        **kwargs
) -> tuple[web.Application, Optional[SQLDatabase]]:
    """
    A webhooks server to receives votes and dispatch them to your bot!
    Go to your bot's edit page on Discord Bot List or Top.gg do add the link and authorization.

    Use :func:`toppy.utils.run_webhook_server` to run the server optionally connect the database.

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
    cache: :class:`bool`
        Whether to cache the votes in a file. Defaults to `False`
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

    if not cache:
        db = None
    else:
        db = SQLDatabase()

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

        if db:
            await db.insert(payload)

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

        if db:
            await db.insert(payload)

        return web.Response(status=200, body=__package__)

    if not application:
        app = web_app_class(**kwargs)
    else:
        app = application

    app.add_routes(routes)

    return app, db
