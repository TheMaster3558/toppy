from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING, TypeVar, Union
import logging
import time

import aiohttp

from .errors import *

if TYPE_CHECKING:
    import asyncio


_log = logging.getLogger(__name__)


K = TypeVar('K')
V = TypeVar('V')


def cleanup_params(params: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in params.items() if v is not None}


# HTTP utils
class RateLimiter:
    def __init__(self, rate: float, per: float):
        self.rate = rate
        self.per = per

        self.count = 0
        self.last_reset = time.time()

    async def check(self):
        if time.time() - self.per > self.last_reset:
            self.count = 0

        if self.count >= self.rate:
            sleep_until = self.last_reset - time.time() - self.per

            if sleep_until <= 0:
                return

            await asyncio.sleep(sleep_until)


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


class TopGGHTTPClient:
    TOPGG_BASE = 'https://top.gg/api'

    def __init__(self, token, *, loop: Optional[asyncio.AbstractEventLoop] = None,
                 session: Optional[aiohttp.ClientSession] = None):
        self.token = token
        self.session = session or aiohttp.ClientSession(loop=loop)

        self.rate_limits: dict[str, RateLimiter] = {
            '/': RateLimiter(100, 1),
            '/bots': RateLimiter(60, 60)
        }

    @property
    def headers(self):
        return {'Authorization': self.token}

    async def check(self, url: str):
        k: str
        v: RateLimiter

        for k, v in self.rate_limits.items():
            if k in url:
                await v.check()

    async def request(self, method: str, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        await self.check(url)
        resp = await self.session.request(method, self.TOPGG_BASE + url, **kwargs, headers=self.headers)
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

    async def search_bots(self, search: str, *, limit: Optional[int] = None,
                          offset: Optional[int] = None) -> list[dict[str, Any]]:
        params = cleanup_params({
            'search': search,
            'limit': limit,
            'offset': offset,
        })
        async with await self.request('GET', '/bots', params=params) as resp:
            data = await resp.json()
        return data.get('results')

    async def search_one_bot(self, bot_id: int, /) -> dict[str, Any]:
        async with await self.request('GET', f'/bots/{bot_id}') as resp:
            return await resp.json()

    async def last_1000_votes(self, bot_id: int, /) -> list[dict[str, Union[str, list[str]]]]:
        async with await self.request('GET', f'/bots/{bot_id}/votes') as resp:
            return await resp.json()

    async def user_vote(self, bot_id: int, user_id: int) -> bool:
        async with await self.request('GET', f'/bots/{bot_id}/check', params={'userId': user_id}) as resp:
            data = await resp.json()
            return data['voted'] is True

    async def post_stats(self, bot_id: int, /, *, server_count: Union[int, list], shard_count: Optional[int] = None
                         ) -> aiohttp.ClientResponse:
        data = cleanup_params({
            'server_count': server_count,
            'shard_count': shard_count
        })
        async with await self.request('POST', f'/bots/{bot_id}/stats', data=data) as resp:
            return resp

