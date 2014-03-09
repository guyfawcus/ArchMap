ArchMap under systemd
=====================

This directory contains two systemd units for running ArchMap automatically under systemd.


Use
---

First we have `archmap.service` which is a regular systemd service with type simple that tries to execute `/usr/bin/archmap.py`, but it doesn't have an `[Install]` section and should thus not be used for automatically generating the geojson file but can be started manually if you want to only try running it once.

Second there is a systemd timer file called `archmap.timer` which once enabled/started will activate the `archmap.service` once every day.
