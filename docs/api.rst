API Reference
==============

Clients
--------

Mixed
~~~~~~

.. autoclass:: toppy.Client
  :members:

Discord Bot List
~~~~~~~~~~~~~~~~~

.. autoclass:: toppy.DiscordBotListClient
  :members:

DiscordBotsGG
~~~~~~~~~~~~~~~~~

.. autoclass:: toppy.DiscordBotsGGClient
  :members:

Top.gg
~~~~~~~~~~~~~~~~~

.. autoclass:: toppy.TopGGClient
  :members:


Cog
----

Use `load_extension('toppy.cog')` to load the cog.

ToppyCog
~~~~~~~~~

.. autoclass:: toppy.cog.ToppyCog
  :members:

Useful Utilities
-----------------

.. autofunction:: toppy.utils.run_web_application

Models
-------
These models represent objects on relavent websites.

Top.gg
~~~~~~~

.. autoclass:: toppy.models.Bot
  :members:

.. autoclass:: toppy.models.User
  :members:
  
Event Reference
----------------

.. function:: on_dbl_post_success()

    Called with a successful post of stats to Discord Bot List has been made.

.. function:: on_dbl_post_error(error)

    Called when an HTTP exception occursed during a post of stats to Discord Bot List.
    
    :param error: The exception that occured.
    :type error: :class:`toppy.HTTPException`
    
.. function:: on_dbgg_post_success()

    Called with a successful post of stats to DiscordBotsGG has been made.

.. function:: on_dbgg_post_error(error)

    Called when an HTTP exception occursed during a post of stats to DiscordBotsGG.
    
    :param error: The exception that occured.
    :type error: :class:`toppy.HTTPException`
    
.. function:: on_topgg_post_success()

    Called with a successful post of stats to Top.gg has been made.

.. function:: on_topgg_post_error(error)

    Called when an HTTP exception occursed during a post of stats to Top.gg.
    
    :param error: The exception that occured.
    :type error: :class:`toppy.HTTPException`

Exceptions
-----------

HTTP Exceptions
~~~~~~~~~~~~~~~~

.. autoclass:: toppy.HTTPException
  :members:
  
.. autoclass:: toppy.BadRequest
  :members:
  
.. autoclass:: toppy.Unauthorized
  :members:
  
.. autoclass:: toppy.Forbidden
  :members:
  
.. autoclass:: toppy.RateLimited
  :members:
  
Missing Extra Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: toppy.MissingExtraRequire
  :members:
  
Client Not Ready
~~~~~~~~~~~~~~~~~~

.. autoclass:: toppy.ClientNotReady
  :members:
  
No Token Set
~~~~~~~~~~~~~~

.. autoclass:: toppy.NoTokenSet
  :members:
