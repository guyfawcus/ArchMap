#!/usr/bin/env python3

from geojson import Feature, Point, FeatureCollection, dumps

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


