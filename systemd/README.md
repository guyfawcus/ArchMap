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


Installation
------------
1. Make sure that you have set up `archmap.conf` in `/etc/` if you aren't going to use the command line options
2. Move the `archmap.service` and `archmap.timer` files to `/etc/systemd/system/`
3. Enable the timer with `systemctl enable archmap.timer` so that it runs automatically after booting
4. Start the timer with `systemctl start archmap.timer` so that it starts now
5. Check that the timer is running with `systemctl list-timers`
