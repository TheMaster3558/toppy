from functools import cached_property


class User:
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

