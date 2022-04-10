"""
toppy
~~~~~~
A simple API wrapper for Top.gg and Discord Bot List
in Python with many *simple* yet powerful features.

:copyright: (c) 2022-present The Master and chawkk6404
:license: MIT
"""

from .client import Client
from .errors import HTTPException, BadRequest, Unauthorized, Forbidden, RateLimited, ClientNotReady

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
    'TopGGClient'
)


__title__ = 'toppy'
__authors__ = ('The Master', 'chawkk6404')
__license__ = 'MIT'
__copyright__ = '2022-present The Master and chawkk6404'
__version__ = '1.1.2'
