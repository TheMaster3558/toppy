from functools import cached_property


__all__ = (
    'User'
)


# much of the doc strings have came from the documentation on Top.gg
class User:
    """
    A class that represents a user from a vote on Top.gg, not any other Top.gg user.
    It will be initialized automatically. Not manually.
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    @cached_property
    def name(self) -> str:
        """
        The username of the user.
        """
        return self._data['str']

    @cached_property
    def id(self) -> int:
        """
          The username of the user.
        """
        return int(self._data['id'])

    @cached_property
    def avatar(self) -> str:
        """
        The avatar hash of the user's avatar
        """
        return self._data['avatar']
