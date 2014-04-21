ArchMap
-------

**archmap.py** generates *geojson* and *kml* files which can be used to display a map of Arch Linux users,
it does this by parsing data from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_.

One rendering of the data is on a map over at
`mapbox.com <https://a.tiles.mapbox.com/v3/alux.hclg4eg0/page.html?secure=1#4/39.63/-104.91>`_ -
This is updated manually so it may be out of date.

Have a look at the `ArchMap <https://wiki.archlinux.org/index.php/ArchMap>`_
page on the ArchWiki for more information about this project.

The documentation is hosted by `readthedocs.org <http://archmap.readthedocs.org>`_ .


Synopsis
--------

By default, running ``./archmap.py`` will output three files to /tmp, ``users.txt``, ``output.geojson`` and ``output.kml``,
this can be overridden by either using the config file or by the command line switches.

The config file should be placed in ``/etc/archmap.conf``, this can be overridden by using ``--config <path-to-config-file>``


Use
---

Running ``./archmap.py --verbose`` wil display this help message::

  archmap.py [-h] [-v] [--config FILE] [--users FILE] [--geojson FILE] [--kml FILE] [--csv FILE] [--geojsonio]

  optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   Show info messages
  --config FILE   Use an alternative configuration file instead of /etc/archmap.conf
  --users FILE    Use FILE for a list of users instead of getting the list from the ArchWiki
  --geojson FILE  Output the geojson to FILE, use 'no' to disable output
  --kml FILE      Output the kml to FILE, use 'no' to disable output
  --csv FILE      Output the csv to FILE, use 'no' to disable output
  --geojsonio     Send the geojson to http://geojson.io for processing


License
-------

Everything in the `ArchMap repo <https://github.com/maelstrom59/ArchMap>`_ is `unicensed <http://unlicense.org/>`_.

All of the files that this script can generate (``users.txt``, ``output.geojson``, ``output.kml``, and ``output.csv``)
will contain text from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_
which puts them under the `GNU Free Documentation License 1.3 or later <http://www.gnu.org/copyleft/fdl.html>`_.
