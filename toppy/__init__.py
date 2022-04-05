"""
toppy
-------------------------------
A simple API wrapper for Top.gg

:copyright: (c) 2022-present The Master
:license: MIT
"""


from .client import TopGGClient, ClientNotReady
from .user import User
from .bot import Bot
from .http import HTTPClient
from .errors import HTTPException, BadRequest, Unauthorized, Forbidden, RateLimited


__all__ = (
    'BadRequest',
    'Bot',
    'ClientNotReady',
    'Forbidden',
    'HTTPClient',
    'HTTPException',
    'RateLimited',
    'TopGGClient',
    'Unauthorized',
    'User'
)


__title__ = 'toppy'
__author__ = 'The Master'
__license__ = 'MIT'
__version__ = '1.0.4'





