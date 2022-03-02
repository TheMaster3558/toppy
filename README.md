# top_gg

A simple API wrapper for Top.gg made in Python.
Specifically meant for discord.py or and similar forks.


## Example

----------
```py
from discord.ext import commands
import top_gg
import aiohttp


dbl_token = 'your token here'

bot = commands.Bot('!')
bot.top_gg = top_gg.TopGGClient(bot, token=dbl_token)


@bot.event
async def on_autopost_success():
    print('Server count posted')
    print(f'Server count: {len(bot.guilds)}')
    

@bot.event
async def on_autopost_error(error: aiohttp.ClientResponseError):
    print(f'Uh oh. An error occurred: {error.message}')
    


bot.run(...)
```

______
## API Reference

### `Client`
A Client to access the Top.gg API. This includes auto-posting Discord Bot Stats
and accessing data about other Discord Bots on Top.gg

https://top.gg/

#### Parameters
`bot`: Positional Only. The Discord Bot instance. Most Clients derived from `discord.Client` will work. \
`token`: Keyword Only. The DBL token found in the Webhooks tab of the bots owner only section. \
`interval`: Keyword Only. The interval in seconds to auto-post the stats.
            Defaults to `600`. \
`post_shard_count`: Keyword Only. Decides whether to post the shard count along with the server count.
            Defaults to `False`. \
`start_on_ready`: Keyword Only. Whether to start the auto post task when the bot is ready.
            If `False` then it must be manually started with `start`
            Defaults to `True` 

#### Methods
`start()`: Starts the auto post task. \
`stop()`: Cancels the task of auto posting stats to Top.gg \
`end()`: `stop` but posts a final time. \
`await search_bots(query: str, *, limit: Optional[int] = None, offset: Optional[int] = None) -> list[Bot]`: Search bots on Top.gg \
`await search_one_bot(bot_id: Union[int, str], /)` Search a single bot on Top.gg
`await last_1000_votes(bot_id: Optional[Union[int, str]] = None, /) -> Generator[User]`: 'Get the last 1000 bots of a bot' \
`await check_if_voted(bot_id: Optional[Union[int, str]], user_id: Union[int, str]) -> bool`: 'Check if a user has voted on a bot' \
`await post_stats()`: Post the bots stats.

### `Bot`
Represents a Bot on Top.gg. **Not** on Discord.

#### Attributes
`id -> str` \
`name -> str` \
`discriminator -> str` \
`avatar -> str` \
`prefix -> str` \
`short_description -> str` \
`long_description -> str` \
`tags -> list[str]` \
`website -> str` \
`support -> str` \
`github -> str` \
`owners -> str` \
`featured_guilds -> list[int]` \
`invite -> str` \
`date -> datetime.datetime` \
`server_count -> Optional[int]` \
`shard_count -> Optional[int]` \
`certified -> bool` \
`vanity -> Optional[str]` \
`upvotes -> int` \
`monthly_upvotes -> int`

### `User`

#### Attributes
`name -> str` \
`id -> int` \
`avatar -> str`





