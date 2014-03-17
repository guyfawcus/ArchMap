#!/usr/bin/env python3

try:
    from systemd import journal
    systemd = True
except:
    systemd = False
from urllib.request import urlopen
from geojson import Feature, Point, FeatureCollection, dumps
try:
    from geojsonio import to_geojsonio
except:
    print("""==> Warning: You need to 'pip install github3.py' and download 'geojsonio.py'
    from https://github.com/jwass/geojsonio.py to this directory
    before you can use --geojsonio\n""")
    geojsonio = False

def message(message):
    if systemd is not False:
        journal.send(message + ".", SYSLOG_IDENTIFIER="ArchMap")
    if args.verbose >= 1:
        print ("==> " + message)

def get_users():
    """This funtion parses users from the ArchWiki and writes it to users.txt"""

    # Open and decode the ArchWiki page containing the list of users.
    message("Getting users from the ArchWiki")
    wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")

    wiki_source = wiki.read().decode()

    # Grab the user data between the second set of <pre> tags.
    wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
    wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
    wiki_text = wiki_source[wiki_text_start:wiki_text_end]

    # Write the user data (wiki_text) to users.txt and close the file.
    message("Writing users to " + output_file_users)
    wiki_output = open(output_file_users, 'w')
    wiki_output.write(wiki_text)
    wiki_output.close()


def make_geojson(geojsonio):
    """This function reads users.txt and outputs output.geojson"""

    # Open files and initialize a list for the geojson features.
    users = open(output_file_users, 'r')
    output = open(output_file_geojson, 'w')

    geo_output = []

    # Loop over the lines in users.txt and assign each element a variable.
    message("Making geosjon")
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

    # Pass the feature collection to geo_output_str.
    geo_output_str = (dumps(FeatureCollection(geo_output)))

    if geojsonio is True:
        # Send the geojson to geojson.io via a GitHub gist.
        message("Sending geojson to geojson.io")
        to_geojsonio(geo_output_str)

    else:
        # Make geo_output_str look pretty.
        message("Tidying up geojson")
        geo_output_str = geo_output_str.replace('"features": [', '"features": [\n')
        geo_output_str = geo_output_str.replace('}}, ', '}},\n')
        geo_output_str = geo_output_str.replace('}}]', '}}\n]')

    # Write geo_output_str to output.geojson.
    message("Writing geojson to " + output_file_geojson)
    output.write(geo_output_str)

    # Close users.txt and output.geojson.
    users.close()
    output.close()


# If the script is being run and not imported, get_users() and make_geojson().
if __name__ == "__main__":
    from argparse import ArgumentParser
    from configparser import ConfigParser

    # Define and parse arguments.
    parser = ArgumentParser(description="ArchMap geojson generator")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show info messages")
    parser.add_argument("--config", metavar="FILE", dest="config_file", default="/etc/archmap.conf",
                        help="Use an alternative configuration file instead of /etc/archmap.conf")
    parser.add_argument("--users", metavar="FILE", dest="users",
                        help="Use FILE for a list of users instead of getting the list from the ArchWiki")
    parser.add_argument("--output", metavar="FILE", dest="output",
                        help="Output the geojson to FILE")
    parser.add_argument("--geojsonio", action="store_true", dest="geojsonio", default="False",
                        help="Send the geojson to http://geojson.io for processing")
    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config_file)
    output_file_geojson = config['files']['geojson']
    output_file_users = config['files']['users']

    if args.users is not None:
        message("Using '" + args.users + "' for user data")
        output_file_users = args.users
    else:
        get_users()

    if args.output is not None:
        output_file_geojson = args.output
    make_geojson(args.geojsonio)
