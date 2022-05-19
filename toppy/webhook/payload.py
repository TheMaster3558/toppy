from __future__ import annotations

from typing import ClassVar, Optional, TYPE_CHECKING, Literal
from datetime import datetime

if TYPE_CHECKING:
    from ..protocols import ClientProtocol, Snowflake


__all__ = (
    'DiscordBotListVotePayload',
    'TopGGVotePayload'
)


# the following documentation has been pulled from the Discord Bot List and Top.gg documentation
class DiscordBotListVotePayload:
    """
    A class to represent the a Discord Bot List webhook payload

    .. versionadded:: 1.3
    """

    SITE: ClassVar[str] = 'Discord Bot List'

    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data
        self.__time = datetime.now()

        self.__user: Optional[Snowflake] = None

    @property
    def time(self) -> datetime:
        return self.__time

    @property
    def raw(self) -> dict:
        """
        Returns the raw data sent.

        Returns
        --------
        :class:`dict`
        """
        return self.__data

    @property
    def admin(self) -> bool:
        """
        If the user is a site administrator for Discord Bot List.

        Returns
        --------
        :class:`bool`
        """
        return self.__data['admin']

    @property
    def avatar(self) -> str:
        """
        The avatar hash of the user.

        Returns
        --------
        :class:`str`
        """
        return self.__data['admin']

    @property
    def username(self) -> str:
        """
        The username of the user who voted.

        Returns
        --------
        :class:`str`
        """
        return self.__data['username']

    @property
    def user_id(self) -> int:
        """
        The ID of the user who voted.

        Returns
        --------
        :class:`int`
        """
        return int(self.__data['id'])

    @property
    def user(self) -> Optional[Snowflake]:
        """
        Returns the :class:`User` object for the user based on what library your client is from.
        If missing use :func:`DiscordBotListVotePayload.fetch()`.

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure `user` is not ``None``.
        """
        self.__user = await self.__client.fetch_user(self.user_id)


class TopGGVotePayload:
    """
    A class to represent the a Top.gg webhook payload

    .. versionadded:: 1.3
    """

    SITE: ClassVar[str] = 'Top.gg'

    def __init__(self, client: ClientProtocol, data: dict):
        self.__client = client
        self.__data = data
        self.__time = datetime.now()

        self.__bot_id: int = data['bot']
        self.__user_id: int = data['user']

        self.__bot: Optional[Snowflake] = None
        self.__user: Optional[Snowflake] = None

    @property
    def time(self) -> datetime:
        return self.__time

    @property
    def raw(self) -> dict:
        """
        Returns the raw data sent.

        Returns
        --------
        :class:`dict`
        """
        return self.__data

    @property
    def bot_id(self) -> int:
        """
        Discord ID of the bot that received a vote.

        Returns
        --------
        :class:`int`
        """
        return self.__bot_id

    @property
    def user_id(self) -> int:
        """
        Discord ID of the user who voted.

        Returns
        --------
        :class:`int`
        """
        return self.__user_id

    @property
    def type(self) -> Literal["upvote", "test"]:
        """
        The type of the vote (should always be "upvote" except when using the test button it's "test").

        Returns
        --------
        Literal["upvote", "test"]
        """
        return self.__data['type']

    @property
    def is_weekend(self) -> bool:
        """
        Whether the weekend multiplier is in effect, meaning users votes count as two.

        Returns
        --------
        :class:`bool`
        """
        return self.__data['isWeekend']

    @property
    def query(self) -> Optional[str]:
        """
        Query string params found on the /bot/:ID/vote page. Example: ?a=1&b=2.

        Returns
        --------
        :class:`str`
        """
        return self.__data.get('query')

    @property
    def bot(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the bot voted for based on what library your client is from.
        If missing use :func:`TopGGVotePayload.fetch()`

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__bot or self.__client.get_user(self.bot_id)

    @property
    def user(self) -> Optional[Snowflake]:
        """
        Returns the ``User`` object for the user based on what library your client is from.
        If missing use :func:`TopGGVotePayload.fetch()`

        Returns
        --------
        Optional[:class:`Snowflake`]
        """
        return self.__user or self.__client.get_user(self.user_id)

    async def fetch(self) -> None:
        """
        Fetches the user id from the Discord API to ensure `TopGGVotePayload.user` and `TopGGVotePayload.bot`
        are not ``None``.
        """
        self.__bot = await self.__client.fetch_user(self.bot_id)
        self.__user = await self.__client.fetch_user(self.user_id)
