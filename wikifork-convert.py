#!/usr/bin/env python3

import urllib.request
from geojson import Feature, Point, FeatureCollection, dumps

wiki = urllib.request.urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")

wiki_source = wiki.read().decode()

wikitext_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
wikitext_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
wikitext = wiki_source[wikitext_start:wikitext_end]

wiki_output = open('wiki-fork', 'w')
wiki_output.write(wikitext)
wiki_output.close()

wikitext = open('wiki-fork', 'r')
output = open('output.geojson', 'w')

geo_output = []

for line in wikitext:
    split = line.split('"')

    coord = split[0].strip(' ')
    coord = coord.split(',')
    name = split[1].strip()

    point = Point((float(coord[1]), float(coord[0])))
    feature = Feature(geometry=point, properties={"Name": name})

    geo_output.append(feature)


output.write(dumps(FeatureCollection(geo_output)))

wikitext.close()
output.close()
