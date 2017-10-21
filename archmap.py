#!/usr/bin/env python3

import logging
from urllib.request import urlopen
import csv

from geojson import Feature, Point, FeatureCollection, dumps
from simplekml import Kml

try:
    from systemd import journal
    systemd = True
except:
    systemd = False


# Define the verbosity level:
# '0' will disable the message printing,
# '1' will enable it.
default_verbosity = 0

# Set the default config file location, this is overridden if the --config switch is used.
# If the --geojson, --kml or --csv switches are used,
# they will override the settings in the config file.
default_config = "/etc/archmap.conf"

# Set the output locations for users, GeoJSON, KML and CSV.
# Setting any of the following to 'no' will disable the output.
# These settings are overridden by the config file, if it exists.
default_users = "/tmp/archmap_users.txt"
default_geojson = "/tmp/archmap.geojson"
default_kml = "/tmp/archmap.kml"
default_csv = "no"


logging.basicConfig(format="==> %(message)s")
log = logging.getLogger("archmap")

if systemd is not False:
    log.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER="archmap"))
    log.handlers[0].setFormatter(logging.Formatter("%(message)s."))


def get_users():
    """This funtion parses the list of users from the ArchWiki and returns it as a string.

    Returns:
        string: The raw text list of users
    """
    # Open and decode the ArchWiki page containing the list of users.
    log.info("Getting users from the ArchWiki")
    wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")
    wiki_source = wiki.read().decode()

    # Grab the user data between the second set of <pre> tags.
    wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
    wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
    wiki_text = wiki_source[wiki_text_start:wiki_text_end] + "\n"

    return wiki_text


def parse_users(users):
    """This function parses the wiki text from ``users`` into it's components.

    Args:
        users (string): Raw user data from the ArchWiki

    Returns:
        list: A list of lists, each sub_list has 4 elements: ``[latitude, longitude, name, comment]``
    """
    users = users.splitlines()
    parsed = []

    log.info("Parsing ArchWiki text")
    for line in users:
        elements = line.split('"')

        coords = elements[0].strip(' ')
        coords = coords.split(',')
        latitude = float(coords[0])
        longitude = float(coords[1])
        name = elements[1].strip()
        comment = elements[2].strip()
        comment = comment[2:]

        parsed.append([latitude, longitude, name, comment])

    return parsed


def make_users(users, output_file):
    """This function reads the raw text supplied by ``users``, it then writes it to ``output_file``.

    Args:
        users (string): The raw text containing the list of users
        output_file (open): Location to save the text output
    """

    log.info("Writing raw user list to " + output_file)
    # Write the text to 'output_file'.
    with open(output_file, 'w') as output:
        output.write(users)


def make_geojson(parsed_users, output_file):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    GeoJSON output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (open): Location to save the GeoJSON output
    """
    geojson = []
    id = 0

    log.info("Making and writing GeoJSON to " + output_file)
    for user in parsed_users:
        # Generate a GeoJSON point feature for the user and add it to 'geojson'.
        point = Point((user[1], user[0]))
        feature = Feature(geometry=point, properties={"Comment": user[3], "Name": user[2]}, id=id)
        geojson.append(feature)

        # Increment the points 'id'.
        id += 1

    # Make 'geojson_str' for output.
    geojson_str = (dumps(FeatureCollection(geojson), sort_keys=True, indent=4)) + "\n"

    output = open(output_file, 'w')
    output.write(geojson_str)
    output.close()


def make_kml(parsed_users, output_file):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    KML output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (open): Location to save the KML output
    """
    kml = Kml()

    log.info("Making and writing KML to " + output_file)
    for user in parsed_users:
        # Generate a KML point for the user.
        kml.newpoint(name=user[2], coords=[(user[1], user[0])], description=user[3])

    kml.save(output_file)


def make_csv(parsed_users, output_file):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    CSV output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (open): Location to save the CSV output
    """
    csvfile = open(output_file, 'w', newline='')
    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

    log.info("Making and writing CSV to " + output_file)
    for user in parsed_users:
        csvwriter.writerow(user)

    csvfile.close()


# If the script is being run and not imported...
if __name__ == "__main__":
    from argparse import ArgumentParser
    from configparser import ConfigParser

    log.setLevel(logging.WARNING)

    # Define and parse arguments.
    parser = ArgumentParser(description="ArchMap GeoJSON/KML generator")
    parser.add_argument('-v', '--verbose', action='count',
                        help="Show info messages")
    parser.add_argument("--config", metavar="FILE", default=default_config,
                        help="Use an alternative configuration file \
                             instead of /etc/archmap.conf")
    parser.add_argument("--users", metavar="FILE",
                        help="Output the user list to FILE, use 'no' to disable output")
    parser.add_argument("--geojson", metavar="FILE",
                        help="Output the GeoJSON to FILE, use 'no' to disable output")
    parser.add_argument("--kml", metavar='FILE',
                        help="Output the KML to FILE, use 'no' to disable output")
    parser.add_argument("--csv", metavar='FILE',
                        help="Output the CSV to FILE, use 'no' to disable output")
    args = parser.parse_args()

    # Try to use the config file. If it doesn't exist, use the defaults.
    try:
        config = ConfigParser()
        config.read(args.config)
        verbosity = int(config['extras']['verbosity'])
        output_file_users = config['files']['users']
        output_file_geojson = config['files']['geojson']
        output_file_kml = config['files']['kml']
        output_file_csv = config['files']['csv']
    except:
        log.warning("Warning: Configuation file error, using defaults")
        verbosity = default_verbosity
        output_file_users = default_users
        output_file_geojson = default_geojson
        output_file_kml = default_kml
        output_file_csv = default_csv

    # Finally, parse the command line arguments, anything passed to them will
    # override both the defaults in this script and anything in the config file.
    if args.verbose is not None:
        verbosity = args.verbose

    if verbosity >= 1:
        log.setLevel(logging.INFO)

    if args.users is not None:
        output_file_users = args.users

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    if args.csv is not None:
        output_file_csv = args.csv

    # Do what's needed.
    if output_file_users == "no" and \
       output_file_geojson == "no" and \
       output_file_kml == "no" and \
       output_file_csv == "no":
        log.warning("There is nothing to do")
    else:
        users = get_users()
        parsed_users = parse_users(users)

        if output_file_users != "no":
            make_users(users, output_file_users)
        if output_file_geojson != "no":
            make_geojson(parsed_users, output_file_geojson)
        if output_file_kml != "no":
            make_kml(parsed_users, output_file_kml)
        if output_file_csv != "no":
            make_csv(parsed_users, output_file_csv)
