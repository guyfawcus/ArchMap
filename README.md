ArchMap
=======

`archmap.py` generates `output.geojson` and `output.kml` which can be used to display a map of Arch Linux users by using data from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List).

One rendering of the data is on a map over at [mapbox.com](https://a.tiles.mapbox.com/v3/alux.hclg4eg0/page.html?secure=1#4/39.63/-104.91) - This is updated manually as is `markers.kml` so it's not as up-to-date as the geojson file `output.geojson`.

Have a look at the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap) page about this project for some more ideas.


Use
----
`./archmp.py --help` will display a help message with all of the available command line options.

To generate a new copy of both `users.txt`, `output.geojson` and `output.kml` simply run `./archmap.py --config <path/to/archmap.config>`, for example, running `./archmap.py --config ./archmap.conf` will make the files in /tmp.
If you pass the `-v` flag, information about what the script is doing will be printed.

You can also `import archmap` in your own python3 code and then use `archmap.get_users()` and `archmap.make_gis()` to make the files yourself.


Copyleft
--------
`archmap.py` and this `README.me` are [unicensed](http://unlicense.org/).

All of the files that this script will generate (`users.txt`, `output.geojson` and `markers.kml`) will contain text from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List) which puts them under the [GNU Free Documentation License 1.3 or later](http://www.gnu.org/copyleft/fdl.html).


Notes
-----
This repo is where [maelstrom59](https://github.com/maelstrom59) started to learn git so please excuse the confusing history!
