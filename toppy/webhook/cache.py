from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

from ..errors import MissingExtraRequire
from ..utils import MISSING

try:
    import aiosqlite
    import aiofiles
except ImportError:
    raise MissingExtraRequire('cache')

if TYPE_CHECKING:
    from .payload import BaseVotePayload


__all__ = (
    'AbstractDatabase',
    'CachedVote',
    'JSONDatabase',
    'SQLiteDatabase'
)


async def mkfile(name: str) -> None:
    async with aiofiles.open(name, 'w'):
        pass


@dataclass(frozen=True)
class CachedVote:
    """
    A dataclass to represent a generic vote.
    """
    number: int
    id: int
    time: datetime
    site: str


@runtime_checkable
class AbstractDatabase(Protocol):
    """A form of database for caching votes.

    This documentation is identical the following:
        :class:`JSONDatabase`
        :class:`SQLiteDatabase`

    .. versionadded:: 1.5
    """

    number: int

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        if not os.path.exists('toppy_vote_cache'):
            os.mkdir('toppy_vote_cache')

        if not os.path.exists('toppy_vote_cache/number.txt'):
            await mkfile('toppy_vote_cache/number.txt')

        async with aiofiles.open('toppy_vote_cache/number.txt', 'r') as f:
            content = await f.read()
            self.number = int(content)

    async def insert(self, payload: BaseVotePayload) -> None:
        """
        Insert a payload into the database.

        Parameters
        -----------
        payload: BaseVotePayload
            The payload to insert.

            .. note::
                This function is usually used internally by in the web application.
        """
        self.number += 1

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
        raise NotImplementedError

    async def fetchmany(self) -> list[CachedVote]:
        """
        Fetch multiple votes. This will be expanded in the future with filters.

        Returns
        --------
        list[:class:`CachedVote`]
        """
        raise NotImplementedError


class SQLiteDatabase(AbstractDatabase):
    """
    A cache for votes using SQLite.
    """
    def __init__(self):
        self.conn: aiosqlite.Connection = MISSING
        self.number: int = 0

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        await super().connect()

        if not os.path.exists('toppy_vote_cache/votes.db'):
            await mkfile('toppy_vote_cache/votes.db')

        self.conn = await aiosqlite.connect('toppy_vote_cache/votes.db')
        await self.conn.execute(
            '''CREATE TABLE IF NOT EXISTS votes(
                        number INT PRIMARY KEY,
                        user_id INT,
                        time TEXT,
                        site TEXT
            );'''
        )
        await self.conn.commit()

    async def insert(self, payload: BaseVotePayload) -> None:
        """
        Insert a payload into the database.

        Parameters
        -----------
        payload: BaseVotePayload
            The payload to insert.

            .. note::
                This function is usually used internally by in the web application.
        """
        await self.conn.execute(
            '''INSERT INTO votes VALUES (
                        ?, ?, ?, ?
            );''',
            (
                self.number,
                payload.user_id,
                payload.time.isoformat(),
                payload.SITE
            )
        )
        await self.conn.commit()

        await super().insert(payload)

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
            data = await cursor.fetchone()

            if not data:
                return None
            number, id, time, site = data

        return CachedVote(
            number,
            id,
            datetime.fromisoformat(time),
            site
        )

    async def fetchmany(self) -> list[CachedVote]:
        """
        Fetch multiple votes. This will be expanded in the future with filters.

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


class JSONDatabase(AbstractDatabase):
    """
    A cache for votes using json.

    .. warning::
        JSON is **not** a proper database and you may have problems with it as your bot grows.
    """
    def __init__(self):
        self.number: int = 0

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        await super().connect()

        if not os.path.exists('toppy_vote_cache/votes.json'):
            async with aiofiles.open('toppy_vote_cache/votes.json', 'w') as f:
                await f.write(json.dumps([]))

    async def insert(self, payload: BaseVotePayload) -> None:
        """
        Insert a payload into the database.

        Parameters
        -----------
        payload: BaseVotePayload
            The payload to insert.

            .. note::
                This function is usually used internally by in the web application.
        """
        async with aiofiles.open('toppy_vote_cache/votes.json', 'r') as f:
            text = await f.read()

        data: list = json.loads(text)
        data.append([
            self.number,
            payload.user_id,
            payload.time.isoformat(),
            payload.SITE
        ])

        async with aiofiles.open('toppy_vote_cache/votes.json', 'w') as f:
            dumped = json.dumps(text, indent=4)
            await f.write(dumped)

        await super().insert(payload)

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
        async with aiofiles.open('toppy_vote_cache/votes.json', 'r') as f:
            text = await f.read()

        data: list = json.loads(text)[number]

        return CachedVote(
            data[0],
            data[1],
            datetime.fromisoformat(data[2]),
            data[3]
        )

    async def fetchmany(self) -> list[CachedVote]:
        """
        Fetch multiple votes. This will be expanded in the future with filters.

        Returns
        --------
        list[:class:`CachedVote`]
        """
        async with aiofiles.open('toppy_vote_cache/votes.json', 'r') as f:
            text = await f.read()

        data: list = json.loads(text)

        return [
            CachedVote(d[0], d[1], datetime.fromisoformat(d[2]), d[3])
            for d in data
        ]
