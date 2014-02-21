#!/usr/bin/env python3

from urllib.request import urlopen
from geojson import Feature, Point, FeatureCollection, dumps

wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")

wiki_source = wiki.read().decode()

wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
wiki_text = wiki_source[wiki_text_start:wiki_text_end]

wiki_output = open('users.txt', 'w')
wiki_output.write(wiki_text)
wiki_output.close()

users = open('users.txt', 'r')
output = open('output.geojson', 'w')

geo_output = []

for line in users:
    elements = line.split('"')

    coords = elements[0].strip(' ')
    coords = coords.split(',')
    latitude = float(coords[0])
    longitude = float(coords[1])
    name = elements[1].strip()
    comment = elements[2].strip()
    comment = comment[2:]

    point = Point((longitude, latitude))
    feature = Feature(geometry=point, properties={"Name": name})

    geo_output.append(feature)


output.write(dumps(FeatureCollection(geo_output)))

users.close()
output.close()
