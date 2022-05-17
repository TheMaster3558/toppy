from __future__ import annotations

from typing import Protocol, Any, Optional, runtime_checkable
import asyncio


__all__ = (
    'ClientProtocol',
    'Snowflake'
)


@runtime_checkable
class Snowflake(Protocol):
    """A protocol that represents the discord snowflake."""
    id: int


@runtime_checkable
class ClientProtocol(Protocol):
    """A bot protocol that allows this library to support forks."""
    loop: asyncio.AbstractEventLoop
    shard_count: Optional[int]

    @property
    def user(self) -> Snowflake: ...

    @property
    def guilds(self) -> Optional[list[Snowflake]]: ...

    @property
    def application_id(self) -> Optional[int]: ...

    @property
    def voice_clients(self) -> list: ...

    @property
    def users(self) -> Optional[list[Snowflake]]: ...

    async def start(self, token: str, *, reconnect: bool = True) -> None: ...

    async def close(self) -> None: ...

    async def wait_until_ready(self) -> None: ...

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None: ...

    def is_closed(self) -> bool: ...

    def get_user(self, user_id: int) -> Snowflake: ...

    async def fetch_user(self, user_id: int) -> Snowflake: ...
