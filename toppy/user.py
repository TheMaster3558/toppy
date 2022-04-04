from functools import cached_property


class User:
    """
    A class that represents a user on Top.gg, not on discord.
    It will be initialized automatically. Not manually.
    """

    __slots__ = ('_data',)

    def __init__(self, data):
        self._data = data

    def __str__(self):
        return self.name

    @cached_property
    def name(self) -> str:
        return self._data['str']

    @cached_property
    def id(self) -> int:
        return int(self._data['id'])

    @cached_property
    def avatar(self) -> str:
        return self._data['avatar']

