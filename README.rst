ArchMap
-------

.. image:: http://img.shields.io/travis/guyfawcus/ArchMap.svg
    :alt: build-status
    :target: https://travis-ci.org/guyfawcus/ArchMap

.. image:: http://img.shields.io/coveralls/guyfawcus/ArchMap.svg
    :alt: coverage
    :target: https://coveralls.io/r/guyfawcus/ArchMap

.. image:: https://img.shields.io/readthedocs/archmap.svg
    :alt: docs-status
    :target: https://readthedocs.org/builds/archmap/

.. image:: http://img.shields.io/badge/license-Unlicense-brightgreen.svg
    :alt: license
    :target: http://unlicense.org/

**archmap** generates *GeoJSON* and *KML* files which can be used to display a map of Arch Linux users,
it does this by parsing data from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_.

Have a look at the `ArchMap <https://wiki.archlinux.org/index.php/ArchMap>`_
page on the ArchWiki for more information about this project.

The documentation is hosted by `readthedocs.org <http://archmap.readthedocs.org>`_.


Installation
------------
You can install ``archmap`` from `PyPi <https://pypi.python.org/pypi?:action=display&name=archmap>`_
by running ``pip3 install archmap`` or from the AUR by installing the
`archmap-git <https://aur.archlinux.org/packages/archmap-git/>`_ package.


Synopsis
--------

By default, running ``archmap`` will output four files to /tmp;
``archmap.txt``, ``archmap.geojson``, ``archmap.kml`` and ``archmap.csv``.
This can be overridden by either using the config file or by the command line switches.

The config file should be placed in ``/etc/archmap.conf``, this can be overridden by using ``--config <path-to-config-file>``


Use
---

Running ``archmap --help`` will display this help message:

.. code-block:: none

  usage:
  archmap [-h] [-v] [-q] [--config FILE] [--url URL] [--file FILE] [--pretty] [--users FILE] [--geojson FILE] [--kml FILE] [--csv FILE]

  optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   Show info messages
  -q, --quiet     Disable info messages
  --config FILE   Use an alternative configuration file instead of /etc/archmap.conf
  --url URL       Use an alternative URL to parse the wiki list from
  --file FILE     Use a file to parse the wiki list from
  --pretty        Prettify the text user list. Only works if user output is enabled
  --users FILE    Output the user list to FILE, use 'no' to disable output or '-' to print to stdout
  --geojson FILE  Output the GeoJSON to FILE, use 'no' to disable output or '-' to print to stdout
  --kml FILE      Output the KML to FILE, use 'no' to disable output or '-' to print to stdout
  --csv FILE      Output the CSV to FILE, use 'no' to disable output or '-' to print to stdout


License
-------

Everything in the `ArchMap repo <https://github.com/guyfawcus/ArchMap>`_ is `unlicensed <http://unlicense.org/>`_.

All of the files that this script can generate (``archmap.txt``, ``archmap.geojson``, ``archmap.kml``, and ``archmap.csv``)
will contain text from the `ArchWiki <https://wiki.archlinux.org/index.php/ArchMap/List>`_
which puts them under the `GNU Free Documentation License 1.3 or later <http://www.gnu.org/copyleft/fdl.html>`_.
