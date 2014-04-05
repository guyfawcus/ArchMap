ArchMap
=======

`archmap.py` generates `output.geojson` and `output.kml` which can be used to display a map of Arch Linux users by using data from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List).

One rendering of the data is on a map over at [mapbox.com](https://a.tiles.mapbox.com/v3/alux.hclg4eg0/page.html?secure=1#4/39.63/-104.91) - This is updated manually as is `markers.kml` so it's not as up-to-date as the geojson file `output.geojson`.

Have a look at the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap) page about this project for some more ideas.


Synopsis
--------
By default, running `./archmap.py` will output three files to /tmp, `users.txt`, `output.geojson` and `output.kml`, this can be overridden by either using the config file or by the command line switches.

The config file should be placed in `/etc/archmap.conf`, this can be overridden by using `--config <path-to-config-file>`


Use
---
    archmap.py [-h] [-v] [--config FILE] [--users FILE] [--geojson FILE] [--kml FILE] [--geojsonio]

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   Show info messages
    --config FILE   Use an alternative configuration file instead of /etc/archmap.conf
    --users FILE    Use FILE for a list of users instead of getting the list from the ArchWiki
    --geojson FILE  Output the geojson to FILE, use 'no' to disable output
    --kml FILE      Output the kml to FILE, use 'no' to disable output
    --geojsonio     Send the geojson to http://geojson.io for processing

Copyleft
--------
`archmap.py` and this `README.me` are [unicensed](http://unlicense.org/).

All of the files that this script will generate (`users.txt`, `output.geojson` and `markers.kml`) will contain text from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List) which puts them under the [GNU Free Documentation License 1.3 or later](http://www.gnu.org/copyleft/fdl.html).


Notes
-----
This repo is where [maelstrom59](https://github.com/maelstrom59) started to learn git so please excuse the confusing history!
