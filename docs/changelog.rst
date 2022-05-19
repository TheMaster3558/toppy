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
    `create_webhook_server` now returns `tuple[aiohttp.web.Application, SQLDatabse]`

New Features
-----------------
1.5.0
    Base classes used now allow easier implementations of new bot websites.

Bug Fixes
-----------------

