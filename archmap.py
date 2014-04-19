#!/usr/bin/env python3

from urllib.request import urlopen
import csv

from geojson import Feature, Point, FeatureCollection, dumps
from simplekml import Kml

try:
    from geojsonio import to_geojsonio
except:
    print("""==> Warning: You need to 'pip install github3.py' and download 'geojsonio.py'
    from https://github.com/jwass/geojsonio.py to this directory
    before you can use --geojsonio\n""")
    geojsonio = False

try:
    from systemd import journal
    systemd = True
except:
    systemd = False


# Set the default config file location, this is overridden if the --config switch is used.
# If the --geojson, --kml or --csv switches are used,
# they will override the settings in the config file.
default_config = "/etc/archmap.conf"

# Set the output locations for users, geojson, kml and csv.
# Setting 'default_geojson', 'default_kml' or 'default_csv' to "no",
# will disable the output.
# These settings are overridden by the config file, if it file exsits.
default_users = "/tmp/users.txt"
default_geojson = "/tmp/output.geojson"
default_kml = "/tmp/output.kml"
default_csv = "no"


def message(message):
    """This function takes a string in 'message'. If the system uses the systemd journal,
    log to it, using 'message'. If the -v or --verbose flag is passed,
    print out 'message'.
    """
    if systemd is not False:
        journal.send(message + ".", SYSLOG_IDENTIFIER="ArchMap")
    if args.verbose >= 1:
        print("==> " + message)


def get_users(output_file):
    """This funtion parses users from the ArchWiki and writes it to 'output_file'"""
    # Open and decode the ArchWiki page containing the list of users.
    message("Getting users from the ArchWiki")
    wiki = urlopen("https://wiki.archlinux.org/index.php/ArchMap/List")
    wiki_source = wiki.read().decode()

    # Grab the user data between the second set of <pre> tags.
    wiki_text_start = wiki_source.find('<pre>', wiki_source.find('<pre>') + 1) + 6
    wiki_text_end = wiki_source.find('</pre>', wiki_source.find('</pre>') + 1) - 1
    wiki_text = wiki_source[wiki_text_start:wiki_text_end]

    # Write the 'wiki_text' to 'output_file'.
    message("Writing users to " + output_file)
    wiki_output = open(output_file, 'w')
    wiki_output.write(wiki_text)
    wiki_output.close()


def parse_users(users_file):
    """This function parses the wiki text from 'users_file' into it's components.
    It returns a list of lists containing the Latitude, Longitude, name and comment
    """
    users = open(users_file, 'r')
    parsed = []

    message("Parsing ArchWiki text")
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


def make_geojson(parsed_users, output_file, send_to_geojsonio):
    """This function reads the user data supplied by 'parsed_users', it then generates
    geojson output and writes it to 'output_file'.

    If you set 'send_to_geojsonio' to 'True' it will send the raw geojson to geojson.io
    via a GitHub gist.

    'parsed_users' should be a list of lists, each sub_list should have 4 elements:
    [0] = latitude, [1] = longitude, [2] = name, [3] = comment.
    """
    message("Making geosjon")

    geojson = []

    for user in parsed_users:
        # Generate a geojson point feature for the user and add it to 'geojson'.
        point = Point((user[1], user[0]))
        feature = Feature(geometry=point, properties={"Comment": user[3], "Name": user[2]})
        geojson.append(feature)

    # Make 'geojson_str' for output.
    geojson_str = (dumps(FeatureCollection(geojson)))

    # Make 'geojson_str' look pretty,
    # then write 'geojson_str_pretty' to 'output_file' if wanted.
    if output_file != "no":
        message("Tidying up geojson")
        geojson_str_pretty = geojson_str
        geojson_str_pretty = geojson_str_pretty.replace('"features": [', '"features": [\n')
        geojson_str_pretty = geojson_str_pretty.replace('}}, ', '}},\n')
        geojson_str_pretty = geojson_str_pretty.replace('}}]', '}}\n]')

        message("Writing geojson to " + output_file)
        output = open(output_file, 'w')
        output.write(geojson_str_pretty)
        output.close()

    # Send the geojson to geojson.io via a GitHub gist if wanted.
    if send_to_geojsonio is True:
        message("Sending geojson to geojson.io")
        to_geojsonio(geojson_str)


def make_kml(parsed_users, output_file):
    """This function reads the user data supplied by 'parsed_users', it then generates
    kml output and writes it to 'output_file'.

    'parsed_users' should be a list of lists, each sub_list should have 4 elements:
    [0] = latitude, [1] = longitude, [2] = name, [3] = comment.
    """
    message("Making and writing kml to " + output_file)

    kml = Kml()

    for user in parsed_users:
        # Generate a kml point for the user.
        kml.newpoint(name=user[2], coords=[(user[1], user[0])], description=user[3])

    kml.save(output_file)


def make_csv(parsed_users, output_file):
    """This function reads the user data supplied by 'parsed_users', it then generates
    csv output and writes it to 'output_file'.

    'parsed_users' should be a list of lists, each sub_list should have 4 elements:
    [0] = latitude, [1] = longitude, [2] = name, [3] = comment.
    """
    message("Making and writing csv to " + output_file)

    csvfile = open(output_file, 'w', newline='')
    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

    for user in parsed_users:
        csvwriter.writerow(user)

    csvfile.close


# If the script is being run and not imported...
if __name__ == "__main__":
    from argparse import ArgumentParser
    from configparser import ConfigParser

    # Define and parse arguments.
    parser = ArgumentParser(description="ArchMap geojson/kml generator")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Show info messages")
    parser.add_argument("--config", metavar="FILE", default=default_config,
                        help="Use an alternative configuration file \
                             instead of /etc/archmap.conf")
    parser.add_argument("--users", metavar="FILE",
                        help="Use FILE for a list of users \
                             instead of getting the list from the ArchWiki")
    parser.add_argument("--geojson", metavar="FILE",
                        help="Output the geojson to FILE, use 'no' to disable output")
    parser.add_argument("--kml", metavar='FILE',
                        help="Output the kml to FILE, use 'no' to disable output")
    parser.add_argument("--csv", metavar='FILE',
                        help="Output the csv to FILE, use 'no' to disable output")
    parser.add_argument("--geojsonio", action="store_true", default=False,
                        help="Send the geojson to http://geojson.io for processing")
    args = parser.parse_args()

    # Try to use the config file. If it doesn't exist, use the defaults.
    try:
        config = ConfigParser()
        config.read(args.config)
        output_file_users = config['files']['users']
        output_file_geojson = config['files']['geojson']
        output_file_kml = config['files']['kml']
        output_file_csv = config['files']['csv']
    except:
        output_file_users = default_users
        output_file_geojson = default_geojson
        output_file_kml = default_kml
        output_file_csv = default_csv

    if args.users is not None:
        message("Using " + args.users + " for user data")
        output_file_users = args.users
    else:
        get_users(output_file_users)

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    if args.csv is not None:
        output_file_csv = args.csv

    # Do what's needed.
    if output_file_geojson == "no" and \
       output_file_kml == "no" and \
       output_file_csv == "no" and \
       args.geojsonio is False:
        message("There is nothing to do")
    else:
        parsed_users = parse_users(output_file_users)
        if output_file_geojson != "no" or args.geojsonio is True:
            make_geojson(parsed_users, output_file_geojson, args.geojsonio)
        if output_file_kml != "no":
            make_kml(parsed_users, output_file_kml)
        if output_file_csv != "no":
            make_csv(parsed_users, output_file_csv)
