from __future__ import annotations

from typing import Protocol, Any, Optional, TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from types import ModuleType


__all__ = (
    'ClientProtocol',
    'Snowflake'
)


class Snowflake(Protocol):
    """A protocol that represents the discord snowflake"""
    id: int


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

    async def wait_until_ready(self) -> None: ...

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None: ...

    def is_closed(self) -> bool: ...
