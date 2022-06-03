from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generator, Generic, Optional, Type, TypeVar

from aiohttp import web

if TYPE_CHECKING:
    from .webhook import AbstractDatabase


__all__ = (
    'MISSING',
    'run_web_application'
)


T = TypeVar('T')
CallableT = TypeVar('CallableT', bound=Callable)


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
    
    
class AsyncContextManager(Generic[T]):
    def __init__(self, awaitable: Awaitable[T]):
        self.awaitable = awaitable
        self.ret: T = MISSING

    def __await__(self) -> Generator[Any, None, T]:
        return self.awaitable.__await__()

    async def __aenter__(self):
        self.ret = await self

        try:
            return await self.ret.__aenter__()
        except AttributeError:
            return self.ret

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            return await self.ret.__aexit__(exc_type, exc_val, exc_tb)
        except AttributeError:
            pass


async def run_web_application(application: web.Application, site_class: Type[web.BaseSite] = web.TCPSite,
                              connect_db: Optional[AbstractDatabase] = None, **kwargs) -> web.BaseSite:
    """
    Run the webhook server created in `create_webhook_server`

    Parameters
    -----------
    application: :class:`aiohttp.web.Application`
        The application to run.
    site_class: :class:`aiohttp.web.BaseSite`
        The site for the application. Must have all methods from :class:`aiohttp.web.BaseSite`.
        Defaults to :class:`web.TCPSite`
    connect_db: Optional[:class:`AbstractDatabase`]
        Pass in an instance that fits the :class:`AbstractDatabase` protocol. This will automatically connect it.
    **kwargs:
        The kwargs to pass into ``site_class``.

    Returns
    --------
    The instance of the site class passed into `site_class`.
    """
    if connect_db is not None:
        await connect_db.connect()

    runner = web.AppRunner(application)
    await runner.setup()

    site = site_class(runner, **kwargs)
    await site.start()

    return site


run_webhook_server = run_web_application


def copy_doc(copy_from: Callable):
    def inner(func: CallableT):
        func.__doc__ = copy_from.__doc__
        return func
    return inner
