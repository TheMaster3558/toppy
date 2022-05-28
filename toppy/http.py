from __future__ import annotations

import asyncio
import logging
import time
from abc import abstractmethod
from typing import Any, Callable, ClassVar, Coroutine, Optional, TypeVar, Union

import aiohttp

from .errors import *
from .utils import AsyncContextManager, MISSING


__all__ = (
    'BaseHTTPClient',
    'DiscordBotListHTTPClient',
    'DiscordBotsGGHTTPClient',
    'TopGGHTTPClient'
)


_log = logging.getLogger(__name__)


K = TypeVar('K')
V = TypeVar('V')


def cleanup_params(params: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in params.items() if v is not None}


class RateLimiter:
    def __init__(self, rate: float, per: float):
        self.rate = rate
        self.per = per

        self.count = 0
        self.last_reset = time.time()

    async def block(self):
        if time.time() - self.per > self.last_reset:
            self.count = 0

        if self.count >= self.rate:
            sleep_until = self.last_reset - time.time() - self.per

            if sleep_until <= 0:
                return

            await asyncio.sleep(sleep_until)


class BaseHTTPClient:
    BASE: ClassVar[str]
    latency: ClassVar[float] = MISSING

    token: str
    session: aiohttp.ClientSession

    def __init__(self, token, *, loop: Optional[asyncio.AbstractEventLoop] = None,
                 session: Optional[aiohttp.ClientSession] = None):
        self.token = token
        self.session = session or aiohttp.ClientSession(loop=loop)

    # method with signature (self, *args, **kwargs) doesn't work
    post_stats: Callable[..., Coroutine[Any, Any, Any]]

    @property
    def headers(self) -> dict:
        return {'Authorization': str(self.token)}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def block(self, url: str):
        pass

    def request(self, method: str, url: str, **kwargs: Any) -> AsyncContextManager[aiohttp.ClientResponse]:
        return AsyncContextManager(self._request(method, url, **kwargs))

    async def _request(self, method: str, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        await self.block(url)
        resp = await self.session.request(method, self.BASE + url, **kwargs, headers=self.headers)

        try:
            data = await resp.json()
        except aiohttp.ContentTypeError:
            data = None
        else:
            async def json(*_, **__):
                return data

            # use only .json() once
            resp.json = json  # type: ignore

        _log.info(
            '%s %s with %s has returned status %d with %s',
            resp.method,
            resp.url,
            kwargs.get('data', kwargs.get('params')),
            resp.status,
            data
        )

        if resp.ok:
            return resp

        if resp.status == 400:
            raise BadRequest(resp)
        elif resp.status == 401:
            raise Unauthorized(resp)
        elif resp.status == 403:
            raise Forbidden(resp)
        elif resp.status == 429:
            _log.warning(
                'Route %s has been ratelimited for %f seconds.',
                data['retry-after']
            )

            if data['retry-after'] <= 60:
                await asyncio.sleep(data['retry-after'])
                return await self._request(method, url, **kwargs)
            raise RateLimited(data['retry-after'], resp)
        raise HTTPException(resp, f'Status: {resp.status}')


class DiscordBotListHTTPClient(BaseHTTPClient):
    BASE = 'https://discordbotlist.com/api/v1'

    async def post_stats(self, bot_id: int, *, voice_connections: int, users: int, guilds: int
                         ) -> None:
        data = {
            'voice_connections': voice_connections,
            'users': users,
            'guilds': guilds
        }

        await self.request('POST', f'/bots/{bot_id}/stats', params=data)


class DiscordBotsGGHTTPClient(BaseHTTPClient):
    Base = 'https://discordbots.gg/api'

    @property
    def headers(self) -> dict:
        return {'Authentication': str(self.token)}

    async def post_stats(self, bot_id: int, guilds: int):
        data = {
            'client_id': bot_id,
            'count': guilds
        }

        await self.request('POST', '/servers', params=data)


class TopGGHTTPClient(BaseHTTPClient):
    BASE = 'https://top.gg/api'

    def __init__(self, token, *, loop: Optional[asyncio.AbstractEventLoop] = None,
                 session: Optional[aiohttp.ClientSession] = None):
        super().__init__(token, loop=loop, session=session)

        self.rate_limits: dict[str, RateLimiter] = {
            '/': RateLimiter(100, 1),
            '/bots': RateLimiter(60, 60)
        }

    async def block(self, url: str) -> None:
        k: str
        v: RateLimiter

        for k, v in self.rate_limits.items():
            if k in url:
                await v.block()

    async def search_bots(self, search: str, *, limit: Optional[int] = None,
                          offset: Optional[int] = None) -> list[dict[str, Any]]:
        params = cleanup_params({
            'search': search,
            'limit': limit,
            'offset': offset,
        })
        async with self.request('GET', '/bots', params=params) as resp:
            data = await resp.json()
        return data['results']

    async def search_one_bot(self, bot_id: int, /) -> dict[str, Any]:
        async with self.request('GET', f'/bots/{bot_id}') as resp:
            return await resp.json()

    async def last_1000_votes(self, bot_id: int, /) -> list[dict[str, Union[str, list[str]]]]:
        async with self.request('GET', f'/bots/{bot_id}/votes') as resp:
            return await resp.json()

    async def user_vote(self, bot_id: int, user_id: int) -> bool:
        async with self.request('GET', f'/bots/{bot_id}/check', params={'userId': user_id}) as resp:
            data = await resp.json()
        return data['voted'] is True

    async def post_stats(self, bot_id: int, *, server_count: Union[int, list], shard_count: Optional[int] = None
                         ) -> None:
        data = cleanup_params({
            'server_count': server_count,
            'shard_count': shard_count
        })
        await self.request('POST', f'/bots/{bot_id}/stats', json=data)
