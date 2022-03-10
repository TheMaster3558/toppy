from typing import TypeVar, Optional, Union, Generator

import aiohttp

from .http import HTTPClient
from .bot import Bot
from .user import User

import asyncio


BotT = TypeVar('BotT')


class TopGGClient:
    def __init__(
            self,
            bot: BotT,
            /,
            token: str,
            *,
            interval: Optional[int] = 600,
            post_shard_count: Optional[bool] = False,
            start_on_ready: Optional[bool] = True
    ):
        """A Client to access the Top.gg API. This includes auto-posting Discord Bot Stats
        and accessing data about other Discord Bots on Top.gg

        https://top.gg/

        Parameters
        ----------
        bot: :class:`discord.Client`
            The Discord Bot instance. Any Client derived from :class:`discord.Client` will work.
        token: :class:`str`
            The DBL token found in the Webhooks tab of the bots owner only section.
        interval: Optional[:class:`int`]
            The interval in seconds to auto-post the stats.
            Defaults to 600.
        post_shard_count: Optional[:class:`bool`]
            Decides whether to post the shard count along with the server count.
            Defaults to False.
        start_on_ready: Optional[:class:`bool`]
            Whether to start the auto post task when the bot is ready.
            If False then it must be manually started with `start`
            Defaults to True

        """
        self.http: HTTPClient = None  # type: ignore
        # filled in on login for the bots user id

        self.token = token
        self.interval = interval
        self.post_shard_count = post_shard_count
        
        if bot.__class__.__name__ == 'CommandTree':
            bot = bot.client
        self.bot = bot
        self.bot.loop.create_task(self.http_init())
        self.task = None

        if start_on_ready:
            self.start()

    def start(self):
        """Starts the autopost task."""
        self.task: asyncio.Task = self.bot.loop.create_task(self._post_task(), 'top_gg_autopost')

    def stop(self):
        """Cancels the task of auto posting stats to Top.gg"""
        self.task.cancel()

    def finish(self):
        """Equivalent to `stop` but posts a final time"""
        self.stop()
        self.bot.loop.create_task(self.post_stats())

    async def http_init(self):
        await self.bot.wait_until_ready()
        self.http = HTTPClient(self.token, self.bot.user.id, loop=self.bot.loop)

    async def search_bots(self, query: str, *, limit: Optional[int] = None, offset: Optional[int] = None
                          ) -> list[Bot]:
        """Search up bots on Top.gg

        Parameters
        ----------
        query: :class:`str`
            The query to use when searching.
        limit: Optional[:class:`int`]
            The limit of :class:`Bot` to return.
            Keyword only.
        offset: Optional[:class:`int`]
            The amount of bots to skip in the results.
            Keyword only.
        ---------
        Returns a list of :class:`Bot`
        """
        raw_bots = await self.http.search_bots(query, limit=limit, offset=offset)
        return [Bot(bot) for bot in raw_bots]

    async def search_one_bot(self, bot_id: Union[int, str], /):
        """Search a single bot on Top.gg

        Parameters
        ----------
        bot_id: Union[:class:`int`, :class:`str`]
            The ID to search.
            Positional only.
        ----------
        Returns :class:`Bot`
        """
        data = await self.http.search_one_bot(bot_id)
        return Bot(data)

    async def last_1000_votes(self, bot_id: Optional[Union[int, str]] = None, /) -> Generator[User]:
        """Get the last 1000 votes of a bot on Top.gg

        Parameters
        ----------
        bot_id: Optional[Union[:class:`int`, :class:`str`]]
            The ID of the bot.
            Defaults to the Bot initialized with.
            Positional only.
        ----------
        Returns a `generator` with :class:`User`
        """
        bot_id = bot_id or self.bot.user.id

        users = await self.http.last_1000_votes(bot_id)
        for user in users:
            yield User(user)

    async def check_if_voted(self, bot_id: Optional[Union[int, str]], user_id: Union[int, str]) -> bool:
        """Check if a user has voted on a bot

        Parameters
        ----------
        bot_id: Optional[Union[:class:`int`, :class:`str`]]
            The ID of the bot.
            Defaults to the Bot initialized with.
        user_id: Union[:class:`int`, :class:`str`]
            The ID of the user.
        """
        bot_id = bot_id or self.bot.user.id

        return await self.http.user_vote(bot_id, user_id)

    async def post_stats(self) -> None:
        """Post your bots stats to Top.gg
        All stats are automatically found and posted

        dispatches `autopost_error` with the argument :class:`aiohttp.ClientResponseError`
        or `autopost_success` with no arguments
        """
        kwargs = {
            'server_count': len(self.bot.guilds)
        }

        if self.post_shard_count:
            kwargs['shard_count'] = self.bot.shard_count

        resp = await self.http.post_stats(self.bot.user.id, **kwargs)
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            self.bot.dispatch('autopost_error', exc)
        else:
            self.bot.dispatch('autopost_success')

    async def _post_task(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.post_stats()
            await asyncio.sleep(self.interval)
