from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING, Union, Any

SPHINX = False
try:
    lib = inspect.getouterframes(inspect.currentframe())[4].filename.split('\\')[-4]
except IndexError:
    # if not extension not loaded properly
    # happens when sphinx docs
    SPHINX = True
    lib = 'discord'

discord: Any = importlib.import_module(lib)
commands: Any = importlib.import_module(f'{lib}.ext.commands')

from .client import Client
from .dbl import DBLClient
from .topgg import TopGGClient

if TYPE_CHECKING:
    import aiohttp

if SPHINX:
    commands.command = lambda **attrs: lambda func: func


class NoTokenSet(Exception):
    def __init__(self):
        message = 'Create a bot var named "topgg_token" or "dbl_token" to use this cog.'
        super().__init__(message)


class ToppyCog(commands.Cog):
    """
    A cog to make it simple to use this library.

    Raises
    -------
    :class:`NoTokenSet` if not token has been set with bot vars.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.client: Union[Client, DBLClient, TopGGClient]

        if hasattr(bot, 'dbl_token') and hasattr(bot, 'topgg_token'):
            self.client = Client(bot, dbl_token=bot.dbl_token, topgg_token=bot.topgg_token)
        elif hasattr(bot, 'dbl_token'):
            self.client = DBLClient(bot, token=bot.dbl_token)
        elif hasattr(bot, 'topgg_token'):
            self.client = TopGGClient(bot, token=bot.topgg_token)
        else:
            raise NoTokenSet()

    @commands.Cog.listener('on_topgg_post_error')
    @commands.Cog.listener('on_dbl_post_error')
    async def post_error(self, error: aiohttp.ClientResponseError):
        print(f'{__name__}: An error occured when posting stats | Status code: {error.status}.'
              f' Enable logging for more information.')

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Catches all errors in this cog raised by `is_owner <https://discordpy.readthedocs.io/en/
        latest/ext/commands/api.html#discord.ext.commands.is_owner>`__
        """

        if isinstance(error, commands.NotOwner):
            return
        raise error

    @commands.command(description='Post the bots stats to DBL, Top.gg, or both.')
    @commands.is_owner()
    async def post(self, ctx: commands.Context, site: str = None):
        """
        A command to post your stats to Discord Bot List, Top.gg, or both.

        ``[p]post [site]``

        site: :class:`str`
            Not required. The site to post to. If not provided it will either post to both or one.

        The `is_owner <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands
        .is_owner>`__ check is used.
        """

        if site is None or not isinstance(self.client, Client):
            await self.client.post_stats()
        elif site.lower() in ('dbl', 'd', 'discordbotlist') and isinstance(self.client, Client):
            await self.client.dbl.post_stats()
        elif site.lower() in ('topgg', 't', 'top.gg') and isinstance(self.client, Client):
            await self.client.topgg.post_stats()
        else:
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

        if isinstance(self.client, Client):
            self.client.intervals = interval  # type: ignore
        else:
            self.client.interval = interval

        await ctx.send(f'Interval changed to {interval}')


if inspect.iscoroutinefunction(commands.Bot.add_cog):  # discord.py uses async setup but some forks don't
    async def setup(bot: commands.Bot) -> None:
        await bot.add_cog(ToppyCog(bot))
else:
    def setup(bot: commands.Bot) -> None:  # type: ignore
        bot.add_cog(ToppyCog(bot))
