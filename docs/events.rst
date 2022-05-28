Event Reference
================

.. code:: py

   async def on_dbl_post_success():
      ...

   async def on_dbl_post_error(error: toppy.HTTPException):
      ...

   async def on_dbl_vote(payload: toppy.DiscordBotListPayload):
      ...

   async def on_dbgg_post_success():
      ...

   async def on_dbgg_post_error(error: toppy.HTTPException):
      ...

   async def on_dbgg_vote(payload: toppy.DiscordBotsGG):
      ...

   async def on_topgg_post_success():
      ...

   async def on_topgg_post_error(error: toppy.HTTPException):
      ...

   async def on_topgg_vote(payload: toppy.TopGGVotePayload):
      ...
