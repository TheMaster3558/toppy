from typing import Optional

from aiohttp import ClientResponse


class HTTPException(Exception):
    """The base HTTP exception class"""
    def __init__(self, resp: Optional[ClientResponse] = None, message: str = None):
        self.resp = resp

        super().__init__(message or ())


class BadRequest(HTTPException):
    """Status 400"""
    pass


class Unauthorized(HTTPException):
    """Status 401"""
    pass


class Forbidden(HTTPException):
    """Status 403"""
    pass


class RateLimited(HTTPException):
    def __init__(self, retry_after: Optional[int] = None, resp: Optional[ClientResponse] = None):
        self.retry_after = retry_after
        super().__init__(resp, f'We have been ratelimited for the next {self.retry_after} seconds.')

