``toppy.webhook`` - Discord Bot List, DiscordBotsGG, and Top.gg webhook servers
================================================================================

Discord Bot List
-----------------
1. Go the edit section of your bot's page

2. Go the the bottom the page to the webhooks section

3. Set ``Upvote Webhook`` to the url your will host the server on

4. Create authorization in ``Webhook Secret``


Top.gg
-------
1. Go the the ``Webhooks`` section of your bot's edit page

2. Set ``Webhook URL`` to the url your will host the server on

4. Create authorization in the ``Authorization`` box


.. note::
  If you would like all requests to be accepted regardless of authorization, set the authorization to ``None``


Reference
------------
.. autoclass:: toppy.webhook.CachedVote
  :members:

.. autofunction:: toppy.webhook.create_webhook_server

.. autoclass:: toppy.webhook.AbstractDatabase
  :members:

.. autoclass:: toppy.webhook.SQLiteDatabase
  :members:
  
.. autoclass:: toppy.webhook.JSONDatabase
  :members:



