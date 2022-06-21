"""
toppy
~~~~~~
An API wrapper made for discord.py or any forks for Discord Bot List, DiscordBotsGG, and/or Top.gg

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client, DiscordBotListClient, DiscordBotsGGClient, TopGGClient
from .errors import (
    BadRequest,
    ClientNotReady,
    Forbidden,
    HTTPException,
    MissingExtraRequire,
    NoTokenSet,
    RateLimited,
    Unauthorized
)
from .models import DiscordBotsGGBot, DiscordBotsGGOwner, TopGGBot, TopGGUser

from . import abc, cog, http, utils


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
    'MissingExtraRequire',
    'NoTokenSet',
    'RateLimited',
    'Unauthorized',
    # models
    'DiscordBotsGGBot',
    'DiscordBotsGGOwner',
    'TopGGBot',
    'TopGGUser'
)


__title__ = 'toppy'
__author__ = 'The Master'
__license__ = 'MIT'
__copyright__ = '2022-present The Master'
__version__ = '2.0.1'
