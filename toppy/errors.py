from typing import Optional

from aiohttp import ClientResponse


__all__ = (
    'ClientNotReady',
    'BadRequest',
    'Forbidden',
    'HTTPException',
    'RateLimited',
    'Unauthorized'
)


class ClientNotReady(Exception):
    def __init__(self):
        message = 'The bot is not ready and does not have an application ID set so no ID could be found'
        super().__init__(message)


class HTTPException(Exception):
    """The base HTTP exception class."""
    def __init__(self, resp: Optional[ClientResponse] = None, message: Optional[str] = None):
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
    def __init__(self, retry_after: Optional[int] = None, resp: Optional[ClientResponse] = None):
        self.retry_after = retry_after
        super().__init__(resp, f'We have been ratelimited for the next {self.retry_after} seconds.')
