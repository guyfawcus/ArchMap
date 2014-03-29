ArchMap under systemd
=====================

This directory contains two systemd units for running ArchMap under systemd to automatically generate new geojson and kml files daily.


Use
---

The first unit is `archmap.service` which is a regular systemd service of type simple that
tries to execute `/usr/bin/archmap.py`. It doesn't have an `[Install]` section because
it's not meant to be used directly, but can be started manually if you want to try running it once.

The Second unit is a systemd timer file called `archmap.timer` which once enabled and started will activate
the `archmap.service` once every day, but waiting until 10 minutes after booting before activating it the first time.
