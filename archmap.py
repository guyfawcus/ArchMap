#!/usr/bin/env python3

from urllib.request import urlopen
from geojson import Feature, Point, FeatureCollection, dumps
from geojsonio import to_geojsonio


def get_users():
    """This funtion parses users from the ArchWiki and writes it to users.txt"""

    # Open and decode the ArchWiki page containing the list of users.
    wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")

    wiki_source = wiki.read().decode()

    # Grab the user data between the second set of <pre> tags.
    wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
    wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
    wiki_text = wiki_source[wiki_text_start:wiki_text_end]

    # Write the user data (wiki_text) to users.txt and close the file.
    wiki_output = open(output_file_users, 'w')
    wiki_output.write(wiki_text)
    wiki_output.close()


def make_geojson():
    """This function reads users.txt and outputs output.geojson"""

    # Open files and initialize a list for the geojson features.
    users = open(output_file_users, 'r')
    output = open(output_file_geojson, 'w')

    geo_output = []

    # Loop over the lines in users.txt and assign each element a variable.
    for line in users:
        elements = line.split('"')

        coords = elements[0].strip(' ')
        coords = coords.split(',')
        latitude = float(coords[0])
        longitude = float(coords[1])
        name = elements[1].strip()
        comment = elements[2].strip()
        comment = comment[2:]

        # Generate a geojson point feature for the entry and add it to geo_output.
        point = Point((longitude, latitude))
        feature = Feature(geometry=point, properties={"Comment": comment, "Name": name})

        geo_output.append(feature)

    # Pass the feature collection to geo_output_str, then make it look pretty.
    geo_output_str = (dumps(FeatureCollection(geo_output)))
    geo_output_str = geo_output_str.replace('"features": [', '"features": [\n')
    geo_output_str = geo_output_str.replace('}}, ', '}},\n')
    geo_output_str = geo_output_str.replace('}}]', '}}\n]')

    # Write geo_output_str to output.geojson.
    output.write(geo_output_str)

    # Send the geojson to geojson.io via a GitHub gist
    to_geojsonio(geo_output_str)

    # Close users.txt and output.geojson.
    users.close()
    output.close()


# If the script is being run and not imported, get_users() and make_geojson().
if __name__ == "__main__":
    from sys import argv
    from configparser import ConfigParser

    # Parse the config file that's given as the first argument to 'archmap.py'.
    if len(argv) == 2:
        config_file = argv[1]
    # ... or read it from /etc
    else:
        config_file = '/etc/archmap.conf'

    config = ConfigParser()
    config.read(config_file)
    output_file_geojson = config['files']['geojson']
    output_file_users = config['files']['users']

    get_users()
    make_geojson()
