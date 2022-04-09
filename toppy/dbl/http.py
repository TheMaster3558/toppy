from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING
import logging

import aiohttp

from ..errors import *

if TYPE_CHECKING:
    import asyncio


__all__ = (
    'DBLHTTPClient'
)


_log = logging.getLogger(__name__)


class DBLHTTPClient:
    DBL_BASE = 'https://discordbotlist.com/api/v1'

    def __init__(self, token, *, loop: Optional[asyncio.AbstractEventLoop] = None,
                 session: Optional[aiohttp.ClientSession] = None):
        self.token = token
        self.session = session or aiohttp.ClientSession(loop=loop)

    @property
    def headers(self):
        return {'Authorization': self.token}

    async def request(self, method: str, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        resp = await self.session.request(method, self.DBL_BASE + url, **kwargs, headers=self.headers)
        json = await resp.json()

        _log.info(f'{resp.method} {resp.url} has returned with {resp.status} {json}')

        if resp.ok:
            return resp

        if resp.status == 400:
            raise BadRequest(resp)
        elif resp.status == 401:
            raise Unauthorized(resp)
        elif resp.status == 403:
            raise Forbidden(resp)
        elif resp.status == 429:
            raise RateLimited(json['retry-after'], resp)
        raise HTTPException()

    async def post_stats(self, bot_id: int, /, *, voice_connections: int, users: int, guilds: int
                         ) -> aiohttp.ClientResponse:
        data = {
            'voice_connections': voice_connections,
            'users': users,
            'guilds': guilds
        }

        async with await self.request('POST', f'/bots/{bot_id}/stats', params=data) as resp:
            return resp
