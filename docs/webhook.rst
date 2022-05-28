``toppy.webhook`` - Discord Bot List and Top.gg webhook servers
================================================================

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


Webhook Server
-------------------
.. automodule:: toppy.webhook.__init__
  :members:


Cache
------
.. automodule:: toppy.cache
  :members:


Vote Payloads
--------------
.. autoclass:: toppy.payload.DiscordBotListVotePayload
  :members:
  :inherited-members:

.. autoclass:: toppy.payload.DiscordBotsGGVotePayload
  :members:
  :inherited-members:

.. autoclass:: toppy.payload.TopGGVotePayload
  :members:
  :inherited-members:


