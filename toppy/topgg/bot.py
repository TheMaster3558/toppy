from __future__ import annotations

from functools import cached_property
from typing import Optional
from datetime import datetime


__all__ = (
    'Bot'
)


# much of the doc strings have came from the documentation on Top.gg
class Bot:
    """
    A class that represents a bot on Top.gg, not on discord.
    It will be initialized automatically. Not manually.
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    @cached_property
    def id(self) -> int:
        """
        The id of the bot.
        """
        return int(self._data['id'])

    @cached_property
    def name(self) -> str:
        """
        The username of the bot.
        """
        return self._data['username']

    @cached_property
    def discriminator(self) -> int:
        """
        The discriminator of the bot.
        """
        return int(self._data['discriminator'])

    @cached_property
    def avatar(self) -> str:
        """
        The avatar hash of the bot's avatar.
        """
        return self._data.get('avatar') or self._data['defAvatar']

    @cached_property
    def prefix(self) -> str:
        """
        The prefix of the bot.
        """
        return self._data['prefix']

    @cached_property
    def short_description(self) -> str:
        """
        The short description of the bot.
        """
        return self._data['shortdesc']

    @cached_property
    def long_description(self) -> str:
        """
        The long description of the bot. Can contain HTML and/or Markdown.
        """
        return self._data['longdesc']

    @cached_property
    def tags(self) -> list[str]:
        """
        The tags of the bot.
        """
        return self._data['tags']

    @cached_property
    def website(self) -> Optional[str]:
        """
        The website url of the bot.
        """
        return self._data.get('website')

    @cached_property
    def support(self) -> Optional[str]:
        """
        The support server invite code of the bot.
        """
        return self._data.get('support')

    @cached_property
    def github(self) -> Optional[str]:
        """
        The link to the github repo of the bot.
        """
        return self._data.get('github')

    @cached_property
    def owners(self) -> list[int]:
        """
        Snowflakes of the owners of the bot. First one in the list is the main owner.
        """
        return [int(owner) for owner in self._data['owners']]

    @cached_property
    def featured_guilds(self) -> list[int]:
        """
        Snowflakes of the guilds featured on the bot page.
        """
        return [int(guild) for guild in self._data['guilds']]

    @cached_property
    def invite(self) -> Optional[str]:
        """
        The custom bot invite url of the bot.
        """
        return self._data.get('invite')

    @cached_property
    def date_of_approval(self) -> datetime:
        """
        The date when the bot was approved.
        """
        return datetime.fromisoformat(self._data['date'])

    @cached_property
    def server_count(self) -> Optional[int]:
        """
        The amount of servers the bot has according to posted stats..
        """
        return self._data.get('server_count')

    @cached_property
    def shard_count(self) -> Optional[int]:
        """
        The amount of shards the bot has according to posted stats..
        """
        return self._data.get('shard_count')

    @cached_property
    def certified(self) -> bool:
        """
        The certified status of the bot.
        """
        return self._data['certifiedBot']

    @cached_property
    def vanity(self) -> Optional[str]:
        """
        The vanity url of the bot.
        """
        return self._data['vanity']

    @cached_property
    def upvotes(self) -> int:
        """
        The amount of upvotes the bot has
        """
        return self._data['points']

    @cached_property
    def monthly_upvotes(self) -> int:
        """
        The amount of upvotes the bot has this month.
        """
        return self._data['monthlyPoints']
