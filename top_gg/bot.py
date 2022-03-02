from functools import cached_property
from typing import Optional
from datetime import datetime


class Bot:
    def __init__(self, data):
        self._data = data

    @cached_property
    def id(self) -> int:
        return int(self._data['id'])

    @cached_property
    def name(self) -> str:
        return self._data['username']

    @cached_property
    def discriminator(self) -> int:
        return int(self._data['discriminator'])

    @cached_property
    def avatar(self) -> str:
        return self._data.get('avatar') or self._data['defAvatar']

    @cached_property
    def prefix(self) -> str:
        return self._data['prefix']

    @cached_property
    def short_description(self) -> str:
        return self._data['shortdesc']

    @cached_property
    def long_description(self) -> str:
        return self._data['longdesc']

    @cached_property
    def tags(self) -> list[str]:
        return self._data['tags']

    @cached_property
    def website(self) -> Optional[str]:
        return self._data.get('website')

    @cached_property
    def support(self) -> Optional[str]:
        return self._data.get('support')

    @cached_property
    def github(self) -> Optional[str]:
        return self._data.get('github')

    @cached_property
    def owners(self) -> list[int]:
        return [int(owner) for owner in self._data['owners']]

    @cached_property
    def featured_guilds(self) -> list[int]:
        return [int(guild) for guild in self._data['guilds']]

    @cached_property
    def invite(self) -> Optional[str]:
        return self._data.get('invite')

    @cached_property
    def date(self) -> datetime:
        return datetime.fromisoformat(self._data['date'])

    @cached_property
    def server_count(self) -> Optional[int]:
        return self._data.get('server_count')

    @cached_property
    def shard_count(self) -> Optional[int]:
        return self._data.get('shard_count')

    @cached_property
    def certified(self) -> bool:
        return self._data['certifiedBot']

    @cached_property
    def vanity(self) -> Optional[str]:
        return self._data['vanity']

    @cached_property
    def upvotes(self) -> int:
        return self._data['points']

    @cached_property
    def monthly_upvotes(self) -> int:
        return self._data['monthlyPoints']
