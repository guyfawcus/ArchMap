Examples
========

All of these example assume you have installed **archmap** via pacman or pip,
if you would like to use the script directly, just use ``./archmap.py``.


Help
----
The **--help** flag will output a help message with all of the available options:

.. code-block:: bash

   archmap --help


Basic use
---------
By default, running **archmap** will output three files to /tmp, **archmap.txt**, **archmap.geojson** and **archmap.kml**,
this can be overridden by either using the config file or by the following command line switches.

Using the **--verbose** flag will print information on what the script is doing:

.. code-block:: bash

   archmap --verbose

You can specify the output location for the user list text, GeoJSON, KML and CSV:

.. code-block:: bash

   archmap --text /tmp/archmap.txt --geojson /tmp/archmap.geojson --kml /tmp/archmap.kml --csv /tmp/archmap.csv


If you would like to parse an alternate copy of the wiki list, simply pass either the --url or --file flags::

    archmap --url https://wiki.archlinux.org/index.php?title=ArchMap/List&oldid=131196

or ::

    archmap --file "$HOME/Downloads/ArchMap_List - ArchWiki.html"

Logging
-------
If the script is run on a system that uses systemd, it will log to it using the syslog identifier - "archmap".

You can review all logs generated by **archmap** by using:

.. code-block:: bash

   journalctl SYSLOG_IDENTIFIER=archmap
