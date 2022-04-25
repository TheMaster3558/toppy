from __future__ import annotations

lib = inspect.getframeinfo(inspect.getouterframes(inspect.currentframe())[1][0])[0]  # get library name
lib = lib.split('/')[-1][:-3]

discord = __import__(lib)
commands = __import__(f'{lib}.ext.commands')

from typing import TYPE_CHECKING
from types import ModuleType
import inspect

from . import Client, TopGGClient, DBLClient

if TYPE_CHECKING:
    discord: ModuleType
    commands: ModuleType


class NoTokenSet(Exception):
    def __init__(self):
        message = 'Create a bot var named "topgg_token" or "dbl_token" to use this cog'
        super().__init__(message)


class ToppyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.client = None
        
        if hasattr(bot, 'dbl_token') and hasattr(bot, 'topgg_token'):
            self.client = Client(bot, dbl_token=bot.dbl_token, topgg_token=bot.topgg_token)  # type: ignore
        elif hasattr(bot, 'dbl_token'):
            self.client = DBLClient(bot, token=bot.dbl_token)  # type: ignore
        elif hasattr(bot, 'topgg_token'):
            self.client = TopGG(bot, token=bot.topgg_token)
        else:
            raise NoTokenSet()
    
    @commands.command()
    @commands.is_owner()
    async def post(ctx: commands.Context, site: str = None) -> None:
        if site is None or not isinstance(self.client, Client):
            await self.client.post_stats()
        elif site.lower() in ('dbl', 'd', 'discordbotlist'):
            await self.client.dbl.post_stats()
        elif site.lower() in ('topgg', 't', 'top.gg'):
            await self.client.topgg.post_stats()
        else:
            await self.client.post_stats()
        
        await ctx.send(f'Stats sucessfully posted.')
            
          
if inspect.iscoroutinefunction(commands.Bot.add_cog):  # discord.py uses async setup but some forks don't
    async def setup(bot: commands.Bot) -> None:
        await bot.add_cog(ToppyCog(bot))
else:
    def setup(bot: commands.Bot) -> None:
        bot.add_cog(ToppyCog(bot))
