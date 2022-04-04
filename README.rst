top_gg
======

A simple API wrapper for Top.gg made in Python.
Specifically meant for discord.py

-----
## Installation
**Python 3.9 or higher is needed**
```shell
pip install -U git+https://github.com/chawkk6404/top_gg
```


Example

----------

.. code:: py
    from discord.ext import commands
    import top_gg
    import aiohttp
    
    
    dbl_token = 'your token here'
    
    bot = commands.Bot('!')  # or discord.Client()
    bot.top_gg = top_gg.TopGGClient(bot, token=dbl_token)
    
    
    @bot.event
    async def on_post_success():
        print('Server count posted')
        print(f'Server count: {len(bot.guilds)}')
    

    @bot.event
    async def on_post_error(error: aiohttp.ClientResponseError):
        print(f'Uh oh. An error occurred: {error.message}')
       
    
    
    bot.run(...)

