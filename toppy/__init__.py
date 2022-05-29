"""
toppy
~~~~~~
An API wrapper made for discord.py or any forks for Discord Bot List and/or Top.gg

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client, DiscordBotListClient, DiscordBotsGGClient, TopGGClient
from .errors import (
    BadRequest,
    ClientNotReady,
    Forbidden,
    HTTPException,
    NoTokenSet,
    RateLimited,
    Unauthorized
)

from . import cog, http, models, protocols, utils


__all__ = (
    # client.py
    'Client',
    'DiscordBotListClient',
    'DiscordBotsGGClient',
    'TopGGClient',
    # errors
    'BadRequest',
    'ClientNotReady',
    'Forbidden',
    'HTTPException',
    'NoTokenSet',
    'RateLimited',
    'Unauthorized'
)


__title__ = 'toppy'
__authors__ = ('The Master', 'chawkk6404')
__license__ = 'MIT'
__copyright__ = '2022-present The Master and chawkk6404'
__version__ = '1.6.1'
