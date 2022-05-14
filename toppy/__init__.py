"""
toppy
~~~~~~
An API wrapper made for discord.py or any forks for Discord Bot List and/or Top.gg

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client, DBLClient, TopGGClient
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
from .webhook import create_webhook_server, DiscordBotListVotePayload, TopGGVotePayload


__all__ = (
    # client.py
    'Client',
    'DBLClient',
    'TopGGClient',
    # errors
    'BadRequest',
    'ClientNotReady',
    'ClientResponseError',
    'Forbidden',
    'HTTPException',
    'NoTokenSet',
    'RateLimited',
    'Unauthorized',
    # webhook.py
    'create_webhook_server',
    'DiscordBotListVotePayload',
    'TopGGVotePayload'
)


__title__ = 'toppy'
__authors__ = ('The Master', 'chawkk6404')
__license__ = 'MIT'
__copyright__ = '2022-present The Master and chawkk6404'
__version__ = '1.4.2'
