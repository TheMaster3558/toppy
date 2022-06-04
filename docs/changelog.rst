Change Log
=========================
Starts after 1.3.7

Breaking Changes
-----------------
1.4.0
    `toppy.dbl` and `toppy.topgg` are now files not modules.

1.4.1
    `run_webhook_server` moved to `toppy.utils`.

1.5.0
    `DiscordBotListClient` and `TopGGClient` have been moved to `toppy.client`.
    `webhook` is now a submodule.
2.0.0
    Most methods removed from `Client` to allow more websites.
    `DBLClient` renamed to `DiscordBotListClient`
    `protocols.py` has been renamed to `abc.py`

New Features
-----------------
1.5.0
    Base classes used now allow easier implementations of new bot websites.
    Cache for webhook votes.

2.0.0
    `discordbotsgg` support added.
    `run_webhook_server` renamed to `run_web_application`

Bug Fixes / Small Changes
--------------------------
1.5.1
    Cog errors now print to `stderr`.
    Fix bug with incorrect error being dispatched.

2.0.0
    Fix bug with incorrect error being dispatched.
