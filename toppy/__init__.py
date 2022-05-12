"""
toppy
~~~~~~
A simple API wrapper for Top.gg and Discord Bot List
in Python with many simple yet powerful features.

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client
from .errors import (
    HTTPException,
    BadRequest,
    Unauthorized,
    Forbidden,
    RateLimited,
    ClientNotReady,
    ClientResponseError,
    NoTokenSet
)
from .webhook import TopGGVotePayload, DiscordBotListVotePayload
from .webhook import create_webhook_server, run_webhook_server

from .dbl import DBLClient
from .topgg import TopGGClient


__all__ = (
    'Client',
    'HTTPException',
    'BadRequest',
    'Unauthorized',
    'Forbidden',
    'RateLimited',
    'ClientNotReady',
    'DBLClient',
    'TopGGClient',
    'TopGGVotePayload',
    'DiscordBotListVotePayload',
    'NoTokenSet',
    'create_webhook_server',
    'run_webhook_server'
)


__title__ = 'toppy'
__authors__ = ('The Master', 'chawkk6404')
__license__ = 'MIT'
__copyright__ = '2022-present The Master and chawkk6404'
__version__ = '1.4.0'
