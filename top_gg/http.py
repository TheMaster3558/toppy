import aiohttp
from typing import Optional, Union, Any
import asyncio


def cleanup_params(params: dict) -> dict:
    return {k: v for k, v in params.items() if v is not None}


class HTTPClient:
    BASE = 'https://top.gg/api'

    def __init__(self, token, bot_id, loop: asyncio.BaseEventLoop = None):
        self.token = token
        self.bot_id = bot_id
        self.session = aiohttp.ClientSession(headers=self.headers, loop=loop)

    @property
    def headers(self):
        return {'Authorization': self.token}

    async def search_bots(self, search: str, *, limit: Optional[str] = None,
                          offset: Optional[int] = None) -> list[dict[str, Any]]:
        params = cleanup_params({
            'search': search,
            'limit': limit,
            'offset': offset,
        })
        async with self.session.get(f'{self.BASE}/bots', params=params) as resp:
            data = await resp.json()
        return data.get('results')

    async def search_one_bot(self, bot_id, /) -> dict[str, Any]:
        async with self.session.get(f'{self.BASE}/bots/{bot_id}') as resp:
            return await resp.json()

    async def last_1000_votes(self, bot_id, /) -> list[dict[str, Union[str, list[str]]]]:
        async with self.session.get(f'{self.BASE}/bots/{bot_id}/votes') as resp:
            return await resp.json()

    async def user_vote(self, bot_id, user_id) -> bool:
        async with self.session.get(f'{self.BASE}/bots/{bot_id}/check', params={'userId': user_id}) as resp:
            data = await resp.json()
            return data['voted'] is True

    async def post_stats(self, bot_id, /, *, server_count: Union[int, list], shard_count: Optional[int] = None
                         ) -> aiohttp.ClientResponse:
        data = cleanup_params({
            'server_count': server_count,
            'shard_count': shard_count
        })
        async with self.session.post(f'{self.BASE}/bots/{bot_id}/stats', data=data) as resp:
            return resp
