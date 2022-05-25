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
    `DBLClient` and `TopGGClient` have been moved to `toppy.client`.
    `webhook` is now a submodule.

New Features
-----------------
1.5.0
    Base classes used now allow easier implementations of new bot websites.
    Cache for webhook votes.

Bug Fixes / Small Changes
-----------------
1.5.1
    Cog errors now print to `stderr`.
    Fix bug with incorrect error being dispatched.
