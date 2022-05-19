from __future__ import annotations

from typing import Union, TYPE_CHECKING, Optional
from dataclasses import dataclass
from datetime import datetime
import os

from ..errors import MissingExtraRequire
from ..utils import MISSING

try:
    import aiosqlite
    import aiofiles
except ModuleNotFoundError:
    raise MissingExtraRequire('cache')

if TYPE_CHECKING:
    from .payload import DiscordBotListVotePayload, TopGGVotePayload


__all__ = (
    'CachedVote',
    'SQLDatabase'
)


@dataclass(frozen=True)
class CachedVote:
    """
    A dataclass to represent a generic vote.
    """
    number: int
    id: int
    time: datetime
    site: str


class SQLDatabase:
    """A form of database for caching votes.

    .. versionadded:: 1.5
    """
    def __init__(self):
        self.conn: aiosqlite.Connection = MISSING
        self.number: int = 0

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        if not os.path.exists('toppy_vote_cache'):
            os.mkdir('toppy_vote_cache')

        if not os.path.exists('toppy_vote_cache/votes.db'):
            os.mknod('toppy_vote_cache/votes.db')

        if not os.path.exists('toppy_vote_cache/number.txt'):
            os.mknod('toppy_vote_cache/number.txt')

        self.conn = await aiosqlite.connect('toppy_vote_cache/votes.db')
        await self.conn.execute(
            '''CREATE TABLE IF NOT EXISTS votes(
                        number INT PRIMARY KEY,
                        id INT,
                        time TEXT,
                        site TEXT
            );'''
        )
        await self.conn.commit()

        async with aiofiles.open('toppy_vote_cache/number.txt', 'r') as f:
            content = await f.read()
            self.number = int(content)

    async def insert(self, payload: Union[DiscordBotListVotePayload, TopGGVotePayload]) -> None:
        """
        Insert a payload into the database.

        Parameters
        -----------
        payload: Union[:class:`DiscordBotListPayload`, :class:`TopGGVotePayload`]
            The payload to insert.

            .. note::
                This function is usually used internally by in the web application.
        """
        self.number += 1

        await self.conn.execute(
            '''INSERT INTO votes VALUES (
                        ?, ?, ?, ?
            );''',
            (
                self.number,
                payload.user_id,
                payload.time,
                payload.SITE
            )
        )
        await self.conn.commit()

        async with aiofiles.open('toppy_vote_cache/number.txt') as f:
            await f.write(str(self.number))

    async def fetchone(self, number: int) -> Optional[CachedVote]:
        """
        Fetch a vote. Use :func:`SQLDatabase.fetchmany` to fetch multiple votes.

        Parameters
        ------------
        number: :class:`int`
            The number in order from least recent to most recent to fetch.

        Returns
        --------
        Optional[:class:`CachedVote`]
        """
        async with self.conn.execute(
                '''SELECT * FROM votes WHERE number = ?;''',
                (number,)
        ) as cursor:
            try:
                number, id, time, site = await cursor.fetchone()
            except TypeError:
                return None

        return CachedVote(
            number,
            id,
            datetime.fromisoformat(time),
            site
        )

    async def fetchmany(self) -> list[CachedVote]:
        """
        Fetch multiple votes. This will be expanded in the future with filters

        Returns
        --------
        list[:class:`CachedVote`]
        """
        async with self.conn.execute(
            '''SELECT * FROM votes;'''
        ) as cursor:
            return [
                CachedVote(number, id, datetime.fromisoformat(time), site)
                async for number, id, time, site in cursor
            ]
