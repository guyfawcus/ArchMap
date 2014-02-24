ArchMap
=======

`archmap.py` generates `output.geojson` which can be used to display a map of Arch Linux users.

User data is from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List).

One rendering of the data is on a map over at [mapbox.com](https://a.tiles.mapbox.com/v3/alux.h81a0lik/page.html?secure=1#3/55.13/21.80) - This is updated manually as is `markers.kml` so it's not as up-to-date as the geojson file `output.geojson`.


Use
----
To generate a new copy of both `users.txt` and `output.geojson` simply run `./archmap.py`.

You can also `import archmap` in your own python3 code and then use `archmap.get_users()` and `archmap.make_geojson()` to make the files yourself.


Copyleft
--------
`archmap.py` and this `README.me` are under the [MIT License](http://opensource.org/licenses/MIT).

`users.txt` contains text from the [ArchWiki](https://wiki.archlinux.org/index.php/ArchMap/List) so it is under the [GNU Free Documentation License 1.3 or later](http://www.gnu.org/copyleft/fdl.html).


Notes
-----
This repo is where [maelstrom59](https://github.com/maelstrom59) started to learn git so please excuse the confusing early history!
