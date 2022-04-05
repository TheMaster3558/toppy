from __future__ import annotations

from typing import Union, Any, Optional
import asyncio
import logging

import aiohttp

from .errors import *


__all__ = (
    'HTTPClient'
)


def cleanup_params(params: dict) -> dict:
    return {k: v for k, v in params.items() if v is not None}


_log = logging.getLogger(__name__)


class HTTPClient:
    BASE = 'https://top.gg/api'

    def __init__(self, token, bot_id, loop: asyncio.AbstractEventLoop = None):
        self.token = token
        self.bot_id = bot_id
        self.session = aiohttp.ClientSession(headers=self.headers, loop=loop)

    @property
    def headers(self):
        return {'Authorization': self.token}

    async def request(self, method: str, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        resp = await self.session.request(method, self.BASE + url, **kwargs)
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

    async def post_stats(self, bot_id, /, *, server_count: Union[int, list], shard_count: Optional[int] = None
                         ) -> aiohttp.ClientResponse:
        data = cleanup_params({
            'server_count': server_count,
            'shard_count': shard_count
        })
        async with await self.request('POST', f'/bots/{bot_id}/stats', data=data) as resp:
            return resp
