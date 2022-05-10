from __future__ import annotations

from typing import Any


__all__ = (
    'MISSING'
)


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
