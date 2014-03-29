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
from simplekml import Kml


# If the system uses the systemd journal, log to it. If the -v or --verbose
# flag is passed, print out info about what the script is doing.
def message(message):
    if systemd is not False:
        journal.send(message + ".", SYSLOG_IDENTIFIER="ArchMap")
    if args.verbose >= 1:
        print("==> " + message)


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


def make_gis(geojsonio):
    """This function reads the user data supplied by get_users(), it then generates
    geojson and kml output and writes it to 'output_file_geojson' and 'output_file_kml'.

    If you set geojsonio to 'True' it will send the raw geojson to geojson.io
    via a GitHub gist."""

    # Open files and initialize a list for the geojson features.
    users = open(output_file_users, 'r')

    geojson = []
    kml = Kml()

    # Loop over the lines in users.txt and assign each element a variable.
    message("Making geosjon and kml")
    for line in users:
        elements = line.split('"')

        coords = elements[0].strip(' ')
        coords = coords.split(',')
        latitude = float(coords[0])
        longitude = float(coords[1])
        name = elements[1].strip()
        comment = elements[2].strip()
        comment = comment[2:]

        # Generate a geojson point feature for the entry and add it to geojson.
        point = Point((longitude, latitude))
        feature = Feature(geometry=point, properties={"Comment": comment, "Name": name})

        geojson.append(feature)

        kml.newpoint(name=name, coords=[(longitude, latitude)], description=comment)

    users.close()

    # Pass the feature collection to geojson_str.
    geojson_str = (dumps(FeatureCollection(geojson)))

    if geojsonio is True:
        # Send the geojson to geojson.io via a GitHub gist.
        message("Sending geojson to geojson.io")
        to_geojsonio(geojson_str)
    else:
        # Make geojson_str look pretty.
        message("Tidying up geojson")
        geojson_str = geojson_str.replace('"features": [', '"features": [\n')
        geojson_str = geojson_str.replace('}}, ', '}},\n')
        geojson_str = geojson_str.replace('}}]', '}}\n]')

    # Write geojson_str to output_file_geojson if wanted.
    if output_file_geojson != "no":
        message("Writing geojson to " + output_file_geojson)
        output = open(output_file_geojson, 'w')
        output.write(geojson_str)
        output.close()

    # Write kml to output_file_kml if wanted.
    if output_file_kml != "no":
        message("Writing kml to " + output_file_kml)
        kml.save(output_file_kml)


# If the script is being run and not imported, get_users(), if it's needed,
# then make_gis().
if __name__ == "__main__":
    from argparse import ArgumentParser
    from configparser import ConfigParser

    # Define and parse arguments.
    parser = ArgumentParser(description="ArchMap geojson/kml generator")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show info messages")
    parser.add_argument("--config", metavar="FILE", dest="config_file", default="/etc/archmap.conf",
                        help="Use an alternative configuration file instead of /etc/archmap.conf")
    parser.add_argument("--users", metavar="FILE", dest="users",
                        help="Use FILE for a list of users instead of getting the list from the ArchWiki")
    parser.add_argument("--geojson", metavar="FILE", dest="geojson",
                        help="Output the geojson to FILE, use 'no' to disable output")
    parser.add_argument("--kml", metavar='FILE', dest="kml",
                        help="Output the kml to FILE, use 'no' to disable output")
    parser.add_argument("--geojsonio", action="store_true", dest="geojsonio", default="False",
                        help="Send the geojson to http://geojson.io for processing")
    args = parser.parse_args()

    try:
        config = ConfigParser()
        config.read(args.config_file)
        output_file_users = config['files']['users']
        output_file_geojson = config['files']['geojson']
        output_file_kml = config['files']['kml']
    except:
        output_file_users = "/tmp/users.txt"
        output_file_geojson = "/tmp/output.geojson"
        output_file_kml = "/tmp/output.kml"

    if args.users is not None:
        message("Using " + args.users + " for user data")
        output_file_users = args.users
    else:
        get_users()

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    make_gis(args.geojsonio)
