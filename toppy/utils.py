from typing import Any


__all__ = (
    'MISSING'  # still shouldn't really be using this
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


MISSING: Any = _MissingSentinel()
