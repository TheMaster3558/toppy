from typing import Union, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

import aiosqlite

from .utils import MISSING

if TYPE_CHECKING:
    from .webhook import DiscordBotListVotePayload, TopGGVotePayload


@dataclass(frozen=True)
class CachedVote:
    id: int
    time: datetime
    site: str


class Database:
    def __init__(self):
        self.conn: aiosqlite.Connection = MISSING

    async def connect(self):
        self.conn = await aiosqlite.connect('./toppy_vote_cache')

        await self.conn.execute(
            '''CREATE TABLE IF NOT EXISTS votes(
                        id INT PRIMARY KEY,
                        time TEXT,
                        site TEXT
            );'''
        )
        await self.conn.commit()

    async def insert(self, payload: Union[DiscordBotListVotePayload, TopGGVotePayload]):
        await self.conn.execute(
            '''INSERT INTO votes VALUES (
                        ?, ?, ?
            );''',
            (
                payload.user_id,
                payload.time,
                payload.SITE
            )
        )
        await self.conn.commit()

    async def fetchone(self, user_id: int) -> CachedVote:
        async with self.conn.execute(
                '''SELECT * FROM votes WHERE id = ?;''',
                (user_id,)
        ) as cursor:
            id, time, site = await cursor.fetchone()

        return CachedVote(
            id,
            datetime.fromisoformat(time),
            site
        )

    async def fetchall(self) -> list[CachedVote]:
        # will be expanded in future with filters
        async with self.conn.execute(
            '''SELECT * FROM votes;'''
        ) as cursor:
            return [
                CachedVote(id, datetime.fromisoformat(time), site)
                async for id, time, site in cursor
            ]
