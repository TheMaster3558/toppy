from __future__ import annotations

from typing import Any, TypeVar


__all__ = (
    'MISSING',
    'cleanup_params',  # still shouldn't really be using this
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


MISSING: Any = _MissingSentinel()


def cleanup_params(params: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in params.items() if v is not None}
