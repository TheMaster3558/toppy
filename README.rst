toppy
======

.. image:: https://raw.githubusercontent.com/chawkk6404/toppy/master/docs/toppy-logo.png
   :alt: toppy logo


An API wrapper made for discord.py or any forks for Discord Bot List, DiscordBotsGG, and Top.gg.


Documentation
--------------
https://toppy-python.readthedocs.io/en/latest/


Installation
------------
**Python 3.8 or higher is needed**

.. code:: sh

    $ pip install -U toppy-python



Example
---------

.. code:: py

    import toppy
    from discord.ext import commands
    

    dbl_token = 'Your Discord Bot List token here'
    dbgg_token = 'Your DiscordBotsGG API token here'
    topgg_token = 'your Top.gg token here'
    
    bot = commands.Bot('!')  # or discord.Client()
    toppy_client = toppy.Client(
        bot,
        dbl_token=dbl_token,
        dbgg_token=dbgg_token,
        topgg_token=topgg_token
    )
    
    
    @bot.event
    async def on_dbl_autopost_success():  # dbl/dbgg/topgg
        print('Server count posted')
        print(f'Server count: {len(bot.guilds)}')
    

    @bot.event
    async def on_dbl_autopost_error(error: toppy.HTTPException):  # dbl/dbgg/topgg
        print(f'Uh oh. An error occurred. Status: {error.resp.status}')
       
    
    
    bot.run(...)

