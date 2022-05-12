"""
toppy
~~~~~~
A simple API wrapper for Top.gg and Discord Bot List
in Python with many simple yet powerful features.

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client
from .dbl import DBLClient
from .errors import (
    BadRequest,
    ClientNotReady,
    ClientResponseError,
    Forbidden,
    HTTPException,
    NoTokenSet,
    RateLimited,
    Unauthorized
)
from .topgg import TopGGClient
from .webhook import create_webhook_server, DiscordBotListVotePayload, TopGGVotePayload


__all__ = (
    # client.py
    'Client',
    # dbl.py
    'DBLClient',
    # errors
    'BadRequest',
    'ClientNotReady',
    'ClientResponseError',
    'Forbidden',
    'HTTPException',
    'NoTokenSet',
    'RateLimited',
    'Unauthorized',
    # topgg.py
    'TopGGClient',
    # webhook.py
    'create_webhook_server',
    'DiscordBotListVotePayload',
    'TopGGVotePayload'
)


__title__ = 'toppy'
__authors__ = ('The Master', 'chawkk6404')
__license__ = 'MIT'
__copyright__ = '2022-present The Master and chawkk6404'
__version__ = '1.4.0'
