# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import geojson

wikitext = open('wiki-fork', 'r')
output = open('output.geojson', 'w')

geo_output = []

for line in wikitext:
    split = line.split('"')

    coord = split[0].strip(' ')
    coord = coord.split(',')
    name = split[1].strip()

    point = Point((float(coord[0]), float(coord[1])))
    feature = Feature(geometry=point, properties={"Name": name})

    geo_output.append(feature)


output.write(geojson.dumps(FeatureCollection(geo_output)))

wikitext.close()
output.close()

# <codecell>


