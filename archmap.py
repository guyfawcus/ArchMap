#!/usr/bin/env python3

from urllib.request import urlopen
import csv

from geojson import Feature, Point, FeatureCollection, dumps
from simplekml import Kml

try:
    from geojsonio import display
    geojsonio = True
except:
    geojsonio = False

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
# Setting 'default_geojson', 'default_kml' or 'default_csv' to "no",
# will disable the output.
# These settings are overridden by the config file, if it file exsits.
default_users = "/tmp/archmap_users.txt"
default_geojson = "/tmp/archmap.geojson"
default_kml = "/tmp/archmap.kml"
default_csv = "no"

# Send the GeoJSON to geojson.io via a GitHub gist,
# anything other than 'no' will enable this feature.
default_geojsonio = "no"


def message(message, verbosity, systemd=systemd):
    """This function is used by others for message printing.

    Args:
        message (string): The text used for logging messages.
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``
        systemd (bool): If not ``False`` (the system uses the systemd journal), it will log to it using ``message``.
    """
    if verbosity >= 1:
        print("==> " + message)
    if systemd is not False:
        journal.send(message + ".", SYSLOG_IDENTIFIER="archmap")


def get_users(output_file, verbosity):
    """This funtion parses users from the ArchWiki and writes it to ``output_file``

    Args:
        output_file (ifile): Location to save the raw user data from the ArchWiki
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``
    """
    # Open and decode the ArchWiki page containing the list of users.
    message("Getting users from the ArchWiki", verbosity)
    wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")
    wiki_source = wiki.read().decode()

    # Grab the user data between the second set of <pre> tags.
    wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
    wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
    wiki_text = wiki_source[wiki_text_start:wiki_text_end] + "\n"

    # Write the 'wiki_text' to 'output_file'.
    message("Writing users to " + output_file, verbosity)
    wiki_output = open(output_file, 'w')
    wiki_output.write(wiki_text)
    wiki_output.close()


def parse_users(users_file, verbosity):
    """This function parses the wiki text from ``users_file`` into it's components.

    Args:
        users_file (file): Raw user data from the ArchWiki
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``

    Returns:
        list: A list of lists, each sub_list has 4 elements: ``[latitude, longitude, name, comment]``
    """
    users = open(users_file, 'r')
    parsed = []

    message("Parsing ArchWiki text", verbosity)
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

    users.close()
    return parsed


def make_geojson(parsed_users, output_file, send_to_geojsonio, verbosity):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    GeoJSON output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (file): Location to save the GeoJSON output
        send_to_geojsonio (bool): If set to ``True`` it will send the GeoJSON to geojson.io via a GitHub gist.
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``
    """
    geojson = []
    id = 0

    message("Making GeoJSON", verbosity)
    for user in parsed_users:
        # Generate a GeoJSON point feature for the user and add it to 'geojson'.
        point = Point((user[1], user[0]))
        feature = Feature(geometry=point, properties={"Comment": user[3], "Name": user[2]}, id=id)
        geojson.append(feature)

        # Increment the points 'id'.
        id += 1

    # Make 'geojson_str' for output.
    geojson_str = (dumps(FeatureCollection(geojson), sort_keys=True, indent=4)) + "\n"

    # Write 'geojson_str' to 'output_file' if wanted.
    if output_file != "no":
        message("Writing GeoJSON to " + output_file, verbosity)
        output = open(output_file, 'w')
        output.write(geojson_str)
        output.close()

    # Send the GeoJSON to geojson.io via a GitHub gist if wanted.
    if send_to_geojsonio is True:
        message("Sending GeoJSON to geojson.io", verbosity)
        display(geojson_str)


def make_kml(parsed_users, output_file, verbosity):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    KML output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (file): Location to save the KML output
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``
    """
    kml = Kml()

    message("Making and writing KML to " + output_file, verbosity)
    for user in parsed_users:
        # Generate a KML point for the user.
        kml.newpoint(name=user[2], coords=[(user[1], user[0])], description=user[3])

    kml.save(output_file)


def make_csv(parsed_users, output_file, verbosity):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    CSV output and writes it to ``output_file``.

    Args:
        parsed_users (list): A list of lists, each sub_list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (file): Location to save the CSV output
        verbosity (int): If set to be >= ``1`` it will print out the string passed to ``message()``
    """
    csvfile = open(output_file, 'w', newline='')
    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

    message("Making and writing CSV to " + output_file, verbosity)
    for user in parsed_users:
        csvwriter.writerow(user)

    csvfile.close()


# If the script is being run and not imported...
if __name__ == "__main__":
    from argparse import ArgumentParser
    from configparser import ConfigParser

    # Define and parse arguments.
    parser = ArgumentParser(description="ArchMap GeoJSON/KML generator")
    parser.add_argument('-v', '--verbose', action='count',
                        help="Show info messages")
    parser.add_argument("--config", metavar="FILE", default=default_config,
                        help="Use an alternative configuration file \
                             instead of /etc/archmap.conf")
    parser.add_argument("--users", metavar="FILE",
                        help="Use FILE for a list of users \
                             instead of getting the list from the ArchWiki")
    parser.add_argument("--geojson", metavar="FILE",
                        help="Output the GeoJSON to FILE, use 'no' to disable output")
    parser.add_argument("--kml", metavar='FILE',
                        help="Output the KML to FILE, use 'no' to disable output")
    parser.add_argument("--csv", metavar='FILE',
                        help="Output the CSV to FILE, use 'no' to disable output")
    parser.add_argument("--geojsonio", action="store_true", default=False,
                        help="Send the GeoJSON to http://geojson.io for processing")
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
        send_to_geojsonio = config['extras']['geojsonio']
    except:
        message("Warning: Configuation file error, using defaults", verbosity=1)
        verbosity = default_verbosity
        output_file_users = default_users
        output_file_geojson = default_geojson
        output_file_kml = default_kml
        output_file_csv = default_csv
        send_to_geojsonio = default_geojsonio

    # Finally, parse the command line arguments, anything passed to them will
    # override both the defaults in this script and anything in the config file.
    if args.verbose is not None:
        verbosity = args.verbose

    if args.users is not None:
        message("Using " + args.users + " for user data", verbosity)
        output_file_users = args.users
    else:
        get_users(output_file_users, verbosity)

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    if args.csv is not None:
        output_file_csv = args.csv

    if args.geojsonio is True:
        send_to_geojsonio = True
    elif send_to_geojsonio != "no":
        send_to_geojsonio = True
    else:
        send_to_geojsonio = False

    # If the geojsonio module was not or could not be imported, print an error message.
    if send_to_geojsonio is True and geojsonio is False:
        message("""Warning: You need to 'pip install github3.py' and download 'geojsonio.py'
                from https://github.com/jwass/geojsonio.py to this directory
                before you can use --geojsonio""", verbosity=1)
        send_to_geojsonio = False

    # Do what's needed.
    if output_file_geojson == "no" and \
       output_file_kml == "no" and \
       output_file_csv == "no" and \
       send_to_geojsonio is False:
        message("There is nothing to do", verbosity)
    else:
        parsed_users = parse_users(output_file_users, verbosity)
        if output_file_geojson != "no" or send_to_geojsonio is True:
            make_geojson(parsed_users, output_file_geojson, send_to_geojsonio, verbosity)
        if output_file_kml != "no":
            make_kml(parsed_users, output_file_kml, verbosity)
        if output_file_csv != "no":
            make_csv(parsed_users, output_file_csv, verbosity)
