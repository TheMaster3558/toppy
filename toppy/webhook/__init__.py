from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Optional, Type

from aiohttp import web

from .cache import AbstractDatabase, CachedVote, JSONDatabase, SQLiteDatabase
from .payload import DiscordBotListVotePayload, DiscordBotsGGVotePayload, TopGGVotePayload
from ..utils import MISSING

if TYPE_CHECKING:
    from ..protocols import ClientProtocol


__all__ = (
    'create_webhook_server',
    # payloads
    'DiscordBotListVotePayload',
    'DiscordBotsGGVotePayload',
    'TopGGVotePayload',
    # databases
    'AbstractDatabase',
    'CachedVote',
    'JSONDatabase',
    'SQLiteDatabase'
)


_log = logging.getLogger(__name__)


def create_webhook_server(
        client: ClientProtocol,
        *,
        dbl_auth: Optional[str] = MISSING,
        dbgg_auth: Optional[str] = MISSING,
        topgg_auth: Optional[str] = MISSING,
        web_app_class: Type[web.Application] = web.Application,
        application: Optional[web.Application] = None,
        db: Optional[AbstractDatabase] = None,
        **kwargs
) -> web.Application:
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
    dbgg_auth: Optional[:class:`str`]
        The DiscordBotGG webhook secret. This can be found in the bots vote settings section.
    topgg_auth: Optional[:class:`str`]
        The Authorization for the webhook. You can make this in the webhooks section of the bot's edit section.
    web_app_class: Type[:class:`aiohttp.web.Application`]
        The web application class to use. Must be derived from :class:`aiohttp.web.Application`.
        If combined with `application` this will be ignored.
    application: :class:`aiohttp.web.Application`
        A pre-existing application to use.
    db: Optional[:class:`AbstractDatabase`]
        The instance of a database. Must fit the :class:`AbstractDatabase` protocol.
    **kwargs:
        Keyword arguments to pass onto `web_app_class`.

    Returns
    --------
    The class from `web_app_class` with the routes added.
    The routes are posts to ``/dbl``, `/dbgg`, or ``/topgg``.


    .. versionadded:: 1.5
        There are now options for a cache.
    """
    if dbl_auth is MISSING:
        dbl_auth = os.urandom(16).hex()
    if dbgg_auth is MISSING:
        dbgg_auth = os.urandom(16).hex()
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
        except json.JSONDecodeError:
            return web.Response(status=400)

        payload = TopGGVotePayload(client, data)
        client.dispatch('dbl_vote', payload)

        if db:
            await db.insert(payload)

        return web.Response(status=200, body=__package__)

    @routes.post('/dbgg')
    async def dbgg_votes(request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400)

        if dbgg_auth is not None:
            if data['secret'] != dbgg_auth:
                return web.Response(status=401)

        payload = DiscordBotsGGVotePayload(client, data)
        client.dispatch('dbgg_vote', payload)

        if db:
            await db.insert(payload)

        return web.Response(status=200, body=__package__)

    @routes.post('/topgg')
    async def topgg_votes(request: web.Request) -> web.Response:
        if topgg_auth is not None:
            if request.headers.get('Authorization') != topgg_auth:
                return web.Response(status=401)

        try:
            data = await request.json()
        except json.JSONDecodeError:
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

    return app
