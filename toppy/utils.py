from __future__ import annotations

from typing import Any, TypeVar
import time
import asyncio


__all__ = (
    'MISSING',
    'RateLimiter'
)


K = TypeVar('K')
V = TypeVar('V')


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return '...'

    def __getattr__(self, item):
        pass


MISSING: Any = _MissingSentinel()


def cleanup_params(params: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in params.items() if v is not None}


# HTTP utils
class RateLimiter:
    def __init__(self, rate: float, per: float):
        self.rate = rate
        self.per = per

        self.count = 0
        self.last_reset = time.time()

    async def check(self):
        if time.time() - self.per > self.last_reset:
            self.count = 0

        if self.count >= self.rate:
            sleep_until = self.last_reset - time.time() - self.per

            if sleep_until <= 0:
                return

            await asyncio.sleep(sleep_until)
