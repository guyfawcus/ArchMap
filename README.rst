ArchMap
-------

.. image:: http://img.shields.io/travis/maelstrom59/ArchMap.svg
    :alt: build-status
    :scale: 100%
    :target: https://travis-ci.org/maelstrom59/ArchMap

.. image:: http://img.shields.io/coveralls/maelstrom59/ArchMap.svg
    :alt: coverage
    :scale: 100%
    :target: https://coveralls.io/r/maelstrom59/ArchMap

.. image:: https://readthedocs.org/projects/archmap/badge/?version=latest
    :alt: docs-status
    :scale: 100%
    :target: https://readthedocs.org/builds/archmap/

.. image:: http://img.shields.io/badge/License-Unlicense-green.svg
    :alt: license
    :scale: 100%
    :target: http://unlicense.org/

**archmap** generates *GeoJSON* and *KML* files which can be used to display a map of Arch Linux users,
it does this by parsing data from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_.

One rendering of the data is on a map over at
`mapbox.com <https://a.tiles.mapbox.com/v3/alux.hclg4eg0/page.html?secure=1#4/39.63/-104.91>`_ -
This is updated manually so it may be out of date.

Have a look at the `ArchMap <https://wiki.archlinux.org/index.php/ArchMap>`_
page on the ArchWiki for more information about this project.

The documentation is hosted by `readthedocs.org <http://archmap.readthedocs.org>`_.


Synopsis
--------

By default, running ``archmap`` will output three files to /tmp, ``archmap_users.txt``, ``archmap.geojson`` and ``archmap.kml``,
this can be overridden by either using the config file or by the command line switches.

The config file should be placed in ``/etc/archmap.conf``, this can be overridden by using ``--config <path-to-config-file>``


Use
---

Running ``archmap --help`` will display this help message::

  archmap [-h] [-v] [--config FILE] [--users FILE] [--geojson FILE] [--kml FILE] [--csv FILE] [--geojsonio]

  optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   Show info messages
  --config FILE   Use an alternative configuration file instead of /etc/archmap.conf
  --users FILE    Use FILE for a list of users instead of getting the list from the ArchWiki
  --geojson FILE  Output the GeoJSON to FILE, use 'no' to disable output
  --kml FILE      Output the KML to FILE, use 'no' to disable output
  --csv FILE      Output the CSV to FILE, use 'no' to disable output
  --geojsonio     Send the GeoJSON to http://geojson.io for processing


License
-------

Everything in the `ArchMap repo <https://github.com/maelstrom59/ArchMap>`_ is `unicensed <http://unlicense.org/>`_.

All of the files that this script can generate (``archmap_users.txt``, ``archmap.geojson``, ``archmap.kml``, and ``archmap.csv``)
will contain text from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_
which puts them under the `GNU Free Documentation License 1.3 or later <http://www.gnu.org/copyleft/fdl.html>`_.
