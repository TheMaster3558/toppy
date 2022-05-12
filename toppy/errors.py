from typing import Optional

import aiohttp


__all__ = (
    'NoTokenSet',
    'ClientResponseError',
    'ClientNotReady',
    'BadRequest',
    'Forbidden',
    'HTTPException',
    'RateLimited',
    'Unauthorized'
)


class NoTokenSet(Exception):
    def __init__(self):
        message = 'Create a bot var named "topgg_token" or "dbl_token" to use this cog.'
        super().__init__(message)


class ClientResponseError(aiohttp.ClientResponseError):
    """An alias of :class:`aiohttp.ClientResponseError`"""


class ClientNotReady(Exception):
    """The bot is not ready and does not have an application ID set so no ID could be found"""
    def __init__(self):
        super().__init__(ClientNotReady.__doc__)


class HTTPException(Exception):
    """The base HTTP exception class."""
    def __init__(self, resp: Optional[aiohttp.ClientResponse] = None, message: Optional[str] = None):
        self.resp = resp

        super().__init__(message or '')


class BadRequest(HTTPException):
    """Status ``400``."""
    pass


class Unauthorized(HTTPException):
    """Status ``401``."""
    pass


class Forbidden(HTTPException):
    """Status ``403``."""
    pass


class RateLimited(HTTPException):
    """Status ``429``."""
    def __init__(self, retry_after: Optional[int] = None, resp: Optional[aiohttp.ClientResponse] = None):
        self.retry_after = retry_after
        super().__init__(resp, f'We have been ratelimited for the next {self.retry_after} seconds.')
