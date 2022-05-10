Quickstart
===========


--------------
Installation
--------------
**Python 3.8 or higher is needed**

.. code:: sh

    $ pip install -U toppy-python



Example
---------

.. code:: py

    from discord.ext import commands
    import toppy
    import aiohttp
    

    dbl_token = 'Your Discord Bot List token here'
    topgg_token = 'your Top.gg token here'
    
    bot = commands.Bot('!')  # or discord.Client()
    toppy_client = toppy.Client(
        bot, dbl_token=dbl_token,
        topgg_token=topgg_token
    )
    
    
    @bot.event
    async def on_dbl_autopost_success():  # or on_topgg_autopost_success
        print('Server count posted')
        print(f'Server count: {len(bot.guilds)}')
    

    @bot.event
    async def on_dbl_autopost_error(error: aiohttp.ClientResponseError):  # or on_topgg_autopost_error
        print(f'Uh oh. An error occurred: {error.message}')
       
    
    
    bot.run(...)
