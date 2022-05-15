from __future__ import annotations

from typing import Any, TypeVar, Type

from aiohttp import web


__all__ = (
    'MISSING',
    'run_webhook_server'
)


BaseSiteT = TypeVar('BaseSiteT', bound=web.BaseSite)


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return '...'

    def __getattr__(self, item):
        pass


MISSING: Any = _MissingSentinel()


async def run_webhook_server(application: web.Application, site_class: Type[BaseSiteT] = web.TCPSite,
                             **kwargs) -> BaseSiteT:
    """
    Run the webhook server created in `create_webhook_server`

    Parameters
    -----------
    application: :class:`aiohttp.web.Application`
        The application to run.
    site_class: :class:`aiohttp.web.BaseSite`
        The site for the application. Must have all methods from :class:`aiohttp.web.BaseSite`.
        Defaults to :class:`web.TCPSite`
    **kwargs:
        The kwargs to pass into `aiohttp.web.TCPSite
        <https://docs.aiohttp.org/en/stable/web_reference.html?highlight=TCPSite>`__

    Returns
    --------
    The instance of the site class passed into `site_class`.
    """
    runner = web.AppRunner(application)
    await runner.setup()

    site = site_class(runner, **kwargs)
    await site.start()

    return site

