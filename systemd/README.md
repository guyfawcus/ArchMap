archmap under systemd
=====================

This directory contains two systemd units for running archmap under systemd to regularly generate new files.


Use
---

The first unit is `archmap.service` which is a regular systemd service of type `simple` that
tries to execute `/usr/bin/archmap`. It doesn't have an `[Install]` section because
it's not meant to be used directly, but can be started manually if you want to try running it once.

The Second unit is a systemd timer file called `archmap.timer` which once enabled and started will activate
the `archmap.service` four times a day starting from 00:00 UTC.
