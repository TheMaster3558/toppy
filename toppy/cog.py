from __future__ import annotations

import importlib
import inspect
import sys
from typing import Any, ClassVar

SPHINX = False
try:
    lib = inspect.getouterframes(inspect.currentframe())[4].filename.split('\\')[-4]
except IndexError:
    # if not extension not loaded properly
    # happens when sphinx docs
    SPHINX = True
    lib = 'discord'

    import warnings
    warnings.warn(
        'You may have tried to load the cog incorrectly. Commands will not work. Use load_extension(\'toppy.cog\')',
        category=UserWarning
    )

discord: Any = importlib.import_module(lib)
commands: Any = importlib.import_module(f'{lib}.ext.commands')     

from .client import Client
from .errors import HTTPException, NoTokenSet

if SPHINX:
    commands.command = lambda **attrs: lambda func: func
    

__all__ = (
    'ToppyCog',
)


class ToppyCog(commands.Cog):
    """
    A cog to make it simple to use this library.

    .. versionadded:: 1.2

    Raises
    -------
    :exc:`toppy.NoTokenSet` if not token has been set with bot vars.
    """
    token_names: ClassVar[tuple] = (
        'dbl_token',
        'dbgg_token',
        'topgg_token'
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        tokens: dict[str, str] = {}
        for token in self.token_names:
            tokens[token] = getattr(bot, token)

        if not tokens:
            raise NoTokenSet()

        self.client: Client = Client(bot, **tokens)

    @commands.Cog.listener('on_topgg_post_error')
    @commands.Cog.listener('on_dbl_post_error')
    @commands.Cog.listener('on_dbgg_post_error')
    async def post_error(self, error: HTTPException):
        """
        This listener will print ``on_topgg_post_error`` and ``on_dbl_post_error`` to the console.
        """
        status = error.resp.status if error.resp else None

        print(f'{__name__}: An error occured when posting stats | Status code: {status}.'
              f' Enable logging for more information.', file=sys.stderr)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Catches all errors in this cog raised by `is_owner <https://discordpy.readthedocs.io/en/
        latest/ext/commands/api.html#discord.ext.commands.is_owner>`__
        """

        if isinstance(error, commands.NotOwner):
            return
        raise error

    @commands.command(description='Post the bots stats.')
    @commands.is_owner()
    async def post(self, ctx: commands.Context):
        """
        A command to post your stats.

        ``[p]post``

        The `is_owner <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands
        .is_owner>`__ check is used.
        """
        await self.client.post_stats()
        await ctx.send('Stats sucessfully posted.')

    @commands.command(description='A command to change the interval of the autopost.')
    @commands.is_owner()
    async def interval(self, ctx: commands.Context, interval: float):
        """
        A command to change the interval of the autopost.

        ``[p]interval <interval>``

        site: :class:`float`
            The interval to change to. If we are using :class:`Client`
            then both Discord Bot List and Top.gg intervals will be changed.
            
        The `is_owner() <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext
        .commands.is_owner>`__ check is used.
        """

        for client in self.client._get_clients():
            client.interval = interval

        await ctx.send(f'Intervals successfully changed to {interval}.')


if inspect.iscoroutinefunction(commands.Bot.add_cog):  # discord.py uses async setup but some forks don't
    async def setup(bot: commands.Bot) -> None:
        await bot.add_cog(ToppyCog(bot))
else:
    def setup(bot: commands.Bot) -> None:  # type: ignore
        bot.add_cog(ToppyCog(bot))
