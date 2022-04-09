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


