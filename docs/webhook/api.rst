.. currentmodule:: toppy.webhook

Webhook API Reference
=======================

.. autofunction:: create_webhook_server

Payloads
----------

.. autoclass:: DiscordBotListVotePayload
  :members:
  :inherited-members:

.. autoclass:: DiscordBotsGGVotePayload
  :members:
  :inherited-members:

.. autoclass:: TopGGVotePayload
  :members:
  :inherited-members:
  
Caching Votes
---------------

.. autoclass:: CachedVote
  :members:

.. autoclass:: AbstractDatabase
  :members:
  :inherited-members:

.. autoclass:: JSONDatabase
  :members:
  :inherited-members:
  
.. autoclass:: SQLiteDatabase
  :members:
  :inherited-members:
  
Event Reference
----------------

.. function:: on_dbl_vote(payload)

    This is called when you have a webhook server made with :func:`create_webhook_server`
    and someone votes for your bot on Discord Bot List.
    
    :param payload: The payload with the vote information.
    :type payload: :class:`DiscordBotListVotePayload`
    
.. function:: on_dbgg_vote(payload)

    This is called when you have a webhook server made with :func:`create_webhook_server`
    and someone votes for your bot on DiscordBotsGG.
    
    :param payload: The payload with the vote information.
    :type payload: :class:`DiscordBotsGGVotePayload`
    
.. function:: on_topgg_vote(payload)

    This is called when you have a webhook server made with :func:`create_webhook_server`
    and someone votes for your bot on Top.gg.
    
    :param payload: The payload with the vote information.
    :type payload: :class:`TopGGVotePayload`
