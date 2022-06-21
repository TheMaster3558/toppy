from __future__ import annotations

import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .abc import Snowflake


__all__ = (
    'DiscordBotsGGBot',
    'DiscordBotsGGOwner',
    'TopGGBot',
    'TopGGUser'
)


class BaseModel:
    id: int

    def __eq__(self, other: Snowflake):
        return self.id == other.id


@dataclass(frozen=True)
class DiscordBotsGGOwner(BaseModel):
    """
    A class that represents an owner of a bot on DiscordBotsGG.

    .. versionchanged:: 2.0.1
        `user_id` renamed to `id`.
    """
    username: str
    discriminator: int
    id: int

    def __str__(self) -> str:
        return f'{self.username}#{self.discriminator}'


class DiscordBotsGGBot(BaseModel):
    """
    A class that represents a bot on DiscordBotsGG, not on discord.

    .. versionadded:: 2.0
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    @property
    def id(self) -> int:
        """
        The id of the bot.
        """
        return self._data['userId']

    @property
    def name(self) -> str:
        """
        The username of the bot.
        """
        return self._data['username']

    @property
    def discriminator(self) -> int:
        """
        The discriminator of the bot.
        """
        return int(self._data['discriminator'])

    @property
    def avatar(self) -> str:
        """
        The avatar url of the bot's avatar.
        """
        return self._data['avatarURL']

    @property
    def co_owners(self) -> list[int]:
        """
        Snowflakes of the co-owners of the bot.
        """
        return self._data['coOwners']

    @property
    def prefix(self) -> str:
        """
        The prefix of the bot.
        """
        return self._data['prefix']

    @property
    def help_command(self) -> str:
        """
        The text to invoke the help command for the bot.
        """
        return self._data['helpCommand']

    @property
    def library_name(self) -> str:
        """
        The library the bot is made with.
        """
        return self._data['libraryName']

    @property
    def website(self) -> str:
        """
        The website url of the bot.
        """
        return self._data['website']

    @property
    def support_invite(self) -> Optional[str]:
        """
        The support server invite code of the bot.
        """
        return self._data['supportInvite']

    @property
    def bot_invite(self) -> str:
        """
        The custom bot invite url of the bot.
        """
        return self._data['supportInvite']

    @property
    def short_description(self) -> str:
        """
        The short description of the bot.
        """
        return self._data['shortdesc']

    @property
    def long_description(self) -> Optional[str]:
        """
        The long description of the bot. Can contain HTML and/or Markdown.
        """
        return self._data.get('longdesc')

    @property
    def open_source(self) -> Optional[str]:
        """
        A url to the code repository of the bot.
        """
        return self._data['openSource']

    @property
    def guild_count(self) -> Optional[int]:
        """
        The amount of guilds the bot has according to posted stats.
        """
        return self._data.get('server_count')

    @property
    def shard_count(self) -> Optional[int]:
        """
        The amount of shards the bot has according to posted stats.
        """
        return self._data.get('shard_count')

    @property
    def verified(self) -> bool:
        """
        Whether the bot has been verified yet.
        """
        return self._data['verified']

    @property
    def online(self) -> bool:
        """
        Whether the bot is online.
        """
        return self._data['online']

    @cached_property
    def in_guild(self) -> bool:
        """
        Whether the bot is in the DiscordBotsGG guild.
        """
        return self._data['inGuild']

    @cached_property
    def owner(self) -> DiscordBotsGGOwner:
        """
        The owner of the bot.
        """
        owner = self._data['owner']
        return DiscordBotsGGOwner(
            owner['username'],
            int(owner['discriminator']),
            int(owner['userId'])
        )

    @property
    def date_of_approval(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._data['addedDate'])

    @property
    def status(self) -> str:
        """
        The current status of the bot.
        """
        return self._data['status']


class TopGGBot(BaseModel):
    """
    A class that represents a bot on Top.gg, not on discord.

    .. versionchanged:: 2.0
        Renamed to `TopGGBot`
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return f'{self.name}#{self.discriminator}'

    @property
    def id(self) -> int:
        """
        The id of the bot.
        """
        return int(self._data['id'])

    @property
    def name(self) -> str:
        """
        The username of the bot.
        """
        return self._data['username']

    @property
    def discriminator(self) -> int:
        """
        The discriminator of the bot.
        """
        return int(self._data['discriminator'])

    @property
    def avatar(self) -> str:
        """
        The avatar hash of the bot's avatar.
        """
        return self._data.get('avatar') or self._data['defAvatar']

    @property
    def prefix(self) -> str:
        """
        The prefix of the bot.
        """
        return self._data['prefix']

    @property
    def short_description(self) -> str:
        """
        The short description of the bot.
        """
        return self._data['shortdesc']

    @property
    def long_description(self) -> str:
        """
        The long description of the bot. Can contain HTML and/or Markdown.
        """
        return self._data['longdesc']

    @property
    def tags(self) -> list[str]:
        """
        The tags of the bot.
        """
        return self._data['tags']

    @property
    def website(self) -> Optional[str]:
        """
        The website url of the bot.
        """
        return self._data.get('website')

    @property
    def support(self) -> Optional[str]:
        """
        The support server invite code of the bot.
        """
        return self._data.get('support')

    @property
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

    @property
    def invite(self) -> Optional[str]:
        """
        The custom bot invite url of the bot.
        """
        return self._data.get('invite')

    @property
    def date_of_approval(self) -> datetime.datetime:
        """
        The date when the bot was approved.
        """
        return datetime.datetime.fromisoformat(self._data['date'])

    @property
    def guild_count(self) -> Optional[int]:
        """
        The amount of guilds the bot has according to posted stats..
        """
        return self._data.get('server_count')

    @property
    def shard_count(self) -> Optional[int]:
        """
        The amount of shards the bot has according to posted stats..
        """
        return self._data.get('shard_count')

    @property
    def certified(self) -> bool:
        """
        The certified status of the bot.
        """
        return self._data['certifiedBot']

    @property
    def vanity(self) -> Optional[str]:
        """
        The vanity url of the bot.
        """
        return self._data['vanity']

    @property
    def upvotes(self) -> int:
        """
        The amount of upvotes the bot has
        """
        return self._data['points']

    @property
    def monthly_upvotes(self) -> int:
        """
        The amount of upvotes the bot has this month.
        """
        return self._data['monthlyPoints']


class TopGGUser(BaseModel):
    """
    A class that represents a user from a vote on Top.gg, not any other Top.gg user.
    It will be initialized automatically. Not manually.

    .. versionchanged:: 2.0
        Renamed to `TopGGUser`
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """
        The username of the user.
        """
        return self._data['str']

    @property
    def id(self) -> int:
        """
          The username of the user.
        """
        return int(self._data['id'])

    @property
    def avatar(self) -> str:
        """
        The avatar hash of the user's avatar
        """
        return self._data['avatar']
