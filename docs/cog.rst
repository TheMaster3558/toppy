``toppy.cog`` - A Cog
=====================


If you just want a simple easy cog to load, you can use this!


1. Add the token bot vars

.. code:: py

    from discord.ext import commands

    bot = commands.Bot('!')

    # we are making bot vars now!
    bot.dbl_token = 'Your Discord Bot List token here'
    bot.dbgg_token = 'Your DiscordBotsGG token here'
    bot.topgg_token = 'Your Top.gg token here'
    # you need at least one token set to work
    # this library will choose the client based off what tokens you pass


2. Load the extension

discord.py's extensions are async but some forks are not.
This library will automatically adjust it based on your library.

.. code:: py

    from discord.ext import commands

    bot = commands.Bot('!')

    # for non async extensions
    bot.load_extension('toppy.cog')

    # for async extensions
    # Option 1: Use the setup_hook
    # Option 2: See below

    import asyncio

    async def main():
        async with bot:
            await bot.load_extension('toppy.cog')
            await bot.start(...)

    asyncio.run(main())
    
    
Cog Reference
--------------

.. autoclass:: toppy.cog.ToppyCog
  :members:
  :undoc-members:
