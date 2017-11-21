#!/usr/bin/env python3
import csv
import logging
import re
from decimal import Decimal
from io import StringIO
from urllib.error import URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup
from geojson import dumps
from geojson import Feature
from geojson import FeatureCollection
from geojson import Point
from simplekml import featgeom
from simplekml import Kml

try:
    from systemd import journal
    systemd = True
except ImportError:
    systemd = False


# Define the verbosity level:
# '0' will disable the message printing,
# '1' will enable it.
default_verbosity = 1

# Set the default config file location, this is overridden if the --config switch is used.
# If the --geojson, --kml or --csv switches are used,
# they will override the settings in the config file.
default_config = '/etc/archmap.conf'

# Define where to get the wiki list from.
# If a file path is supplied to 'default_file', it will be used instead of the URL
default_url = 'https://wiki.archlinux.org/index.php/ArchMap/List'
default_file = ''

# Set the output locations for users, GeoJSON, KML and CSV.
# Setting any of the following to 'no' will disable the output.
# These settings are overridden by the config file, if it exists.
default_users = '/tmp/archmap_users.txt'
default_geojson = '/tmp/archmap.geojson'
default_kml = '/tmp/archmap.kml'
default_csv = '/tmp/archmap.csv'


logging.basicConfig(format='==> %(message)s')
log = logging.getLogger('archmap')
log.setLevel(logging.WARNING)

if systemd is not False:
    log.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER='archmap'))
    log.handlers[0].setFormatter(logging.Formatter('%(message)s.'))


def get_users(url='https://wiki.archlinux.org/index.php/ArchMap/List', local=''):
    """This funtion parses the list of users from the ArchWiki and returns it as a string.

    Args:
        url (str): Link to a URL that points to a ArchWiki ArchMap list (default)
        local (str): Path to a local copy of the ArchWiki ArchMap source

    Returns:
        str or None: The extracted raw text list of users or None if not avaliable
    """
    if local == '':
        # Open and decode the page from the URL containing the list of users.
        log.info('Getting users from the ArchWiki: {}'.format(url))
        try:
            wiki = urlopen(url)
            wiki_source = wiki.read().decode()
        except URLError:
            log.critical("Can't connect to the ArchWiki")
            return None

    else:
        # Open and decode the local page containing the list of users.
        with open(local, 'r') as wiki:
            log.info('Getting users from a local file: {}'.format(local))
            wiki_source = wiki.read()

    # Grab the user data between the second set of <pre> tags.
    soup = BeautifulSoup(wiki_source, 'html.parser')
    wiki_text = soup.find_all('pre')[1].text.strip()

    return wiki_text


def parse_users(users):
    """This function parses the wiki text from ``users`` into it's components.

    Args:
        users (str): Raw user data from the ArchWiki

    Returns:
        :obj:`list` of :obj:`list` [:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`]\
        : A list of lists, each sub-list has 4 elements: ``[latitude, longitude, name, comment]``
    """
    users = users.splitlines()
    parsed = []

    # Expression that matches one-half of a coordinate pair. Results in 3 groups: Full, before decimal and after decimal
    re_coord = r'((\-?\d+)\.*(\d+)?)'

    # Expression that matches the name inside the quote marks and puts that into a group
    re_name = r'"(.*)"'

    # Expression that puts the comment in a group
    re_comment = r'(.*)'

    # Compiled expression that combines all of the groups with the stuff inbetween. Results in 8 groups:
    #     1. Full latitude
    #     2. Latitude before decimal
    #     3. Latitude after decimal
    #     4. Full longitude
    #     5. Longitude before decimal
    #     6. Longitude after decimal
    #     7. Name
    #     8. Comment
    re_whole = re.compile(str(re_coord + r'\s*,\s*' + re_coord + r'[^a-zA-Z]*' + re_name + r'\s*#*\s*' + re_comment))

    log.info('Parsing ArchWiki text')
    for line in users:
        # Retun None unless the line fully matches the RE
        re_whole_result = re_whole.fullmatch(line)

        if re_whole_result:
            latitude = Decimal(re_whole_result.group(1))
            longitude = Decimal(re_whole_result.group(4))
            name = re_whole_result.group(7).strip()
            comment = re_whole_result.group(8).strip()

            parsed.append([latitude, longitude, name, comment])

        else:
            log.error('Bad line: {}'.format(line))

    return parsed


def make_users(parsed_users, output_file='', pretty=False):
    """This function reads the raw text supplied by ``users``, it then writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`list` [:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`])\
        : A list of lists, each sub-list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (str): Location to save the text output. If left empty, nothing will be output
        pretty (bool): If set to True, the output "columns" will be aligned and expanded to match the longest element

    Returns:
        str: The text written to the output file
    """
    users = ''

    longest_latitude = 1
    longest_longitude = 1
    longest_name = 1
    longest_comment = 1

    if pretty:
        log.debug('Finding longest strings for prettying the raw user list')
        # Go through all of the elements in each list and track the length of the longest string
        for user in parsed_users:
            latitude = user[0]
            longitude = user[1]
            name = user[2]
            comment = user[3]

            if longest_latitude < len(str(latitude)):
                longest_latitude = len(str(latitude))
            if longest_longitude < len(str(longitude)):
                longest_longitude = len(str(longitude))
            if longest_name < len(str(name)):
                longest_name = len(str(name))
            if longest_comment < len(str(comment)):
                longest_comment = len(str(comment))

    log.debug('Making raw users')
    for user in parsed_users:
        latitude = user[0]
        longitude = user[1]
        name = user[2]
        comment = user[3]

        # This follows the formatting defined here:
        #     https://wiki.archlinux.org/index.php/ArchMap/List#Adding_yourself_to_the_list
        #
        # If pretty printing is enabled, the 'longest_' lengths are used to align the elements in the string
        # Change the '<', '^' or '>' to change the justification (< = left, > = right, ^ = center)
        users += '{:<{}},{:<{}} "{:^{}}" # {:>{}}\n'.format(latitude, longest_latitude,
                                                            longitude, longest_longitude,
                                                            name, longest_name,
                                                            comment, longest_comment)

    # If the last user didnt have a comment, go back to that line
    # and strip the trailing whitespace then replace the newline (prevents editor errors)
    users = users.strip('\n').strip() + '\n'

    if output_file != '':
        log.info('Writing raw user list to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(users)

    return users


def make_geojson(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    GeoJSON output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`list` [:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`])\
        : A list of lists, each sub-list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (str): Location to save the GeoJSON output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    geojson = []

    log.debug('Making GeoJSON')
    for id, user in enumerate(parsed_users):
        # Generate a GeoJSON point feature for the user and add it to 'geojson'.
        point = Point((float(user[1]), float(user[0])))
        feature = Feature(geometry=point, properties={'Comment': user[3], 'Name': user[2]}, id=id)
        geojson.append(feature)

    # Make 'geojson_str' for output.
    geojson_str = (dumps(FeatureCollection(geojson), sort_keys=True, indent=4)) + '\n'

    if output_file != '':
        log.info('Writing GeoJSON to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(geojson_str)

    return geojson_str


def make_kml(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    KML output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`list` [:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`])\
        : A list of lists, each sub-list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (str): Location to save the KML output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    kml = Kml()

    log.debug('Making KML')
    for user in parsed_users:
        # Generate a KML point for the user.
        kml.newpoint(name=user[2], coords=[(user[1], user[0])], description=user[3])

    # Reset the ID counters
    featgeom.Feature._id = 0
    featgeom.Geometry._id = 0

    kml_str = kml.kml()

    if output_file != '':
        log.info('Writing KML to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(kml_str)

    return kml_str


def make_csv(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    CSV output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`list` [:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`])\
        : A list of lists, each sub-list should have 4 elements: ``[latitude, longitude, name, comment]``
        output_file (str): Location to save the CSV output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    log.debug('Making CSV')
    csv_string = StringIO()
    csv_string_writer = csv.writer(csv_string, quoting=csv.QUOTE_MINIMAL, dialect='unix')
    csv_string_writer.writerow(['Latitude', 'Longitude', 'Name', 'Comment'])
    for user in parsed_users:
        csv_string_writer.writerow(user)

    csv_str = csv_string.getvalue()
    csv_string.close()

    if output_file != '':
        log.info('Writing CSV to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(csv_str)

    return csv_str


def main():
    from argparse import ArgumentParser
    from configparser import ConfigParser

    # Define and parse arguments.
    parser = ArgumentParser(description='ArchMap GeoJSON/KML generator')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Show info messages')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Disable info messages')
    parser.add_argument('--config', metavar='FILE', default=default_config,
                        help='Use an alternative configuration file \
                             instead of /etc/archmap.conf')
    parser.add_argument('--url', metavar='URL',
                        help='Use an alternative URL to parse the wiki list from')
    parser.add_argument('--file', metavar='FILE',
                        help='Use a file to parse the wiki list from')
    parser.add_argument('--users', metavar='FILE',
                        help="Output the user list to FILE, use 'no' to disable output")
    parser.add_argument('--geojson', metavar='FILE',
                        help="Output the GeoJSON to FILE, use 'no' to disable output")
    parser.add_argument('--kml', metavar='FILE',
                        help="Output the KML to FILE, use 'no' to disable output")
    parser.add_argument('--csv', metavar='FILE',
                        help="Output the CSV to FILE, use 'no' to disable output")
    args = parser.parse_args()

    # Try to use the config file. If it doesn't exist, use the defaults.
    try:
        config = ConfigParser()
        config.read(args.config)
        verbosity = int(config['extras']['verbosity'])
        input_url = config['files']['url']
        input_file = config['files']['file']
        output_file_users = config['files']['users']
        output_file_geojson = config['files']['geojson']
        output_file_kml = config['files']['kml']
        output_file_csv = config['files']['csv']
    except Exception as e:
        log.warning('Warning: Configuation file error: {}. Using defaults'.format(e))
        verbosity = default_verbosity
        input_url = default_url
        input_file = default_file
        output_file_users = default_users
        output_file_geojson = default_geojson
        output_file_kml = default_kml
        output_file_csv = default_csv

    # Finally, parse the command line arguments, anything passed to them will
    # override both the defaults in this script and anything in the config file.
    if args.verbose is not None:
        verbosity = args.verbose

    if verbosity == 1:
        log.setLevel(logging.INFO)

    if verbosity > 1:
        log.setLevel(logging.DEBUG)

    if args.quiet or verbosity == -1:
        log.setLevel(logging.CRITICAL)

    if args.url is not None:
        input_url = args.url

    if args.file is not None:
        input_file = args.file

    if args.users is not None:
        output_file_users = args.users

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    if args.csv is not None:
        output_file_csv = args.csv

    # Do what's needed.
    dont_run = ['', 'no']
    if output_file_users in dont_run and \
       output_file_geojson in dont_run and \
       output_file_kml in dont_run and \
       output_file_csv in dont_run:
        log.warning('There is nothing to do')
    else:
        users = get_users(url=input_url, local=input_file)
        if users is None:
            return None
        parsed_users = parse_users(users)

        if output_file_users not in dont_run:
            make_users(parsed_users, output_file_users)
        if output_file_geojson not in dont_run:
            make_geojson(parsed_users, output_file_geojson)
        if output_file_kml not in dont_run:
            make_kml(parsed_users, output_file_kml)
        if output_file_csv not in dont_run:
            make_csv(parsed_users, output_file_csv)


# If the script is being run and not imported...
if __name__ == '__main__':
    main()
