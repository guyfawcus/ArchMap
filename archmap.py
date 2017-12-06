#!/usr/bin/env python3
import csv
import logging
import re
from collections import namedtuple
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

# If set to True, the columns in the raw-text list will be aligned
default_pretty = False

# Set the output locations for the raw-text, GeoJSON, KML and CSV files.
# Setting any of the following to 'no' or leaving it blank will disable the output,
# use '-' to print the generated text to stdout.
# These settings are overridden by the config file, if it exists.
default_text = '/tmp/archmap.txt'
default_geojson = '/tmp/archmap.geojson'
default_kml = '/tmp/archmap.kml'
default_csv = '/tmp/archmap.csv'


logging.basicConfig(format='==> %(message)s')
log = logging.getLogger('archmap')
log.setLevel(logging.WARNING)

if systemd is not False:
    log.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER='archmap'))
    log.handlers[0].setFormatter(logging.Formatter('%(message)s.'))

# Define the namedtuple used to store each users details
Entry = namedtuple(typename='Entry', field_names=['latitude', 'longitude', 'name', 'comment'])


def get_users(url='https://wiki.archlinux.org/index.php/ArchMap/List', local=''):
    """This funtion parses the list of users from the ArchWiki and returns it as a string.

    Args:
        url (str): Link to a URL that points to a ArchWiki ArchMap list (default)
        local (str): Path to a local copy of the ArchWiki ArchMap source

    Returns:
        str or None: The extracted raw-text list of users or None if not avaliable
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

    # Grab the user data between the last set of <pre> tags.
    soup = BeautifulSoup(wiki_source, 'html.parser')
    wiki_text = soup.find_all('pre')[-1].text.strip()

    return wiki_text


def parse_users(users):
    """This function parses the raw-text list (``users``) that has been extracted from the wiki page
    and splits it into a list of namedtuples containing the latitude, longitude, name and comment.

    Args:
        users (str): raw-text list from the ArchWiki

    Returns:
        :obj:`list` of :obj:`collections.namedtuple` \
        (:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`)\
        : A list of namedtuples, each namedtuple has 4 elements: ``(latitude, longitude, name, comment)``
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

    log.info('Parsing ArchWiki list')
    for line_number, line in enumerate(users, start=1):
        # Retun None unless the line fully matches the RE
        re_whole_result = re_whole.fullmatch(line)

        if re_whole_result:
            latitude = Decimal(re_whole_result.group(1))
            longitude = Decimal(re_whole_result.group(4))
            name = re_whole_result.group(7).strip()
            comment = re_whole_result.group(8).strip()

            parsed.append(Entry(latitude=latitude, longitude=longitude, name=name, comment=comment))

        else:
            log.error('Bad line ({}): {}'.format(line_number, line))

    return parsed


def make_text(parsed_users, output_file='', pretty=False):
    """This function reads the user data supplied by ``parsed_users``, it then generates a raw-text list
    according to the formatting specifications on the wiki and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`collections.namedtuple` \
        (:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`))\
        : A list of namedtuples, each namedtuple should have 4 elements: ``(latitude, longitude, name, comment)``
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
        log.debug('Finding longest strings for prettifying the raw-text')
        # Go through all of the elements in each list and track the length of the longest string
        for user in parsed_users:
            if longest_latitude < len(str(user.latitude)):
                longest_latitude = len(str(user.latitude))
            if longest_longitude < len(str(user.longitude)):
                longest_longitude = len(str(user.longitude))
            if longest_name < len(str(user.name)):
                longest_name = len(str(user.name))
            if longest_comment < len(str(user.comment)):
                longest_comment = len(str(user.comment))

    log.debug('Making raw-text')
    for user in parsed_users:
        # This follows the formatting defined here:
        #     https://wiki.archlinux.org/index.php/ArchMap/List#Adding_yourself_to_the_list
        #
        # If pretty printing is enabled, the 'longest_' lengths are used to align the elements in the string
        # Change the '<', '^' or '>' to change the justification (< = left, > = right, ^ = center)
        users += '{:<{}},{:<{}} "{:^{}}" # {:>{}}\n'.format(user.latitude, longest_latitude,
                                                            user.longitude, longest_longitude,
                                                            user.name, longest_name,
                                                            user.comment, longest_comment)

    # If the last user didnt have a comment, go back to that line
    # and strip the trailing whitespace then replace the newline (prevents editor errors)
    users = users.strip('\n').strip() + '\n'

    if output_file == '-':
        print(users)

    elif output_file != '':
        log.info('Writing raw-text to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(users)

    return users


def make_geojson(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    GeoJSON output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`collections.namedtuple` \
        (:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`))\
        : A list of namedtuples, each namedtuple should have 4 elements: ``(latitude, longitude, name, comment)``
        output_file (str): Location to save the GeoJSON output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    geojson = []

    log.debug('Making GeoJSON')
    for id, user in enumerate(parsed_users):
        # Generate a GeoJSON point feature for the user and add it to 'geojson'.
        point = Point((float(user.longitude), float(user.latitude)))
        feature = Feature(geometry=point, properties={'Name': user.name, 'Comment': user.comment}, id=id)
        geojson.append(feature)

    # Make 'geojson_str' for output.
    geojson_str = (dumps(FeatureCollection(geojson), sort_keys=True, indent=4)) + '\n'

    if output_file == '-':
        print(geojson_str)

    elif output_file != '':
        log.info('Writing GeoJSON to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(geojson_str)

    return geojson_str


def make_kml(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    KML output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`collections.namedtuple` \
        (:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`))\
        : A list of namedtuples, each namedtuple should have 4 elements: ``(latitude, longitude, name, comment)``
        output_file (str): Location to save the KML output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    kml = Kml()

    log.debug('Making KML')
    for user in parsed_users:
        # Generate a KML point for the user.
        kml.newpoint(coords=[(user.longitude, user.latitude)], name=user.name, description=user.comment)

    # Reset the ID counters
    featgeom.Feature._id = 0
    featgeom.Geometry._id = 0

    kml_str = kml.kml()

    if output_file == '-':
        print(kml_str)

    elif output_file != '':
        log.info('Writing KML to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(kml_str)

    return kml_str


def make_csv(parsed_users, output_file=''):
    """This function reads the user data supplied by ``parsed_users``, it then generates
    CSV output and writes it to ``output_file``.

    Args:
        parsed_users (:obj:`list` of :obj:`collections.namedtuple` \
        (:obj:`decimal.Decimal`, :obj:`decimal.Decimal`, :obj:`str`, :obj:`str`))\
        : A list of namedtuples, each namedtuple should have 4 elements: ``(latitude, longitude, name, comment)``
        output_file (str): Location to save the CSV output. If left empty, nothing will be output

    Returns:
        str: The text written to the output file
    """
    log.debug('Making CSV')
    csv_string = StringIO()
    csv_string_writer = csv.writer(csv_string, quoting=csv.QUOTE_MINIMAL, dialect='unix')
    csv_string_writer.writerow(('Latitude', 'Longitude', 'Name', 'Comment'))
    for user in parsed_users:
        csv_string_writer.writerow((user.latitude, user.longitude, user.name, user.comment))

    csv_str = csv_string.getvalue()
    csv_string.close()

    if output_file == '-':
        print(csv_str)

    elif output_file != '':
        log.info('Writing CSV to ' + output_file)
        with open(output_file, 'w') as output:
            output.write(csv_str)

    return csv_str


def main():
    from argparse import ArgumentParser
    from configparser import ConfigParser
    from pathlib import Path

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
    parser.add_argument('--pretty', action='store_true',
                        help='Prettify the raw-text. Only works if user output is enabled')
    parser.add_argument('--text', metavar='FILE',
                        help="Output the raw-text to FILE, use 'no' to disable output or '-' to print to stdout")
    parser.add_argument('--geojson', metavar='FILE',
                        help="Output the GeoJSON to FILE, use 'no' to disable output or '-' to print to stdout")
    parser.add_argument('--kml', metavar='FILE',
                        help="Output the KML to FILE, use 'no' to disable output or '-' to print to stdout")
    parser.add_argument('--csv', metavar='FILE',
                        help="Output the CSV to FILE, use 'no' to disable output or '-' to print to stdout")
    args = parser.parse_args()

    config_location = Path(args.config)
    config = ConfigParser()

    # Try to use the config file. If it doesn't exist, use the defaults.
    if not config_location.is_file():
        log.warning('Warning: Configuation file does not exist. Using defaults')
    else:
        config.read(str(config_location))

    verbosity = config.getint('extras', 'verbosity', fallback=default_verbosity)
    pretty = config.getboolean('extras', 'pretty', fallback=default_pretty)
    input_url = config.get('files', 'url', fallback=default_url)
    input_file = config.get('files', 'file', fallback=default_file)
    output_file_text = config.get('files', 'text', fallback=default_text)
    output_file_geojson = config.get('files', 'geojson', fallback=default_geojson)
    output_file_kml = config.get('files', 'kml', fallback=default_kml)
    output_file_csv = config.get('files', 'csv', fallback=default_csv)

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

    if args.pretty is not False:
        pretty = True

    if args.url is not None:
        input_url = args.url

    if args.file is not None:
        input_file = args.file

    if args.text is not None:
        output_file_text = args.text

    if args.geojson is not None:
        output_file_geojson = args.geojson

    if args.kml is not None:
        output_file_kml = args.kml

    if args.csv is not None:
        output_file_csv = args.csv

    # Do what's needed.
    dont_run = ['', 'no']
    if output_file_text in dont_run and \
       output_file_geojson in dont_run and \
       output_file_kml in dont_run and \
       output_file_csv in dont_run:
        log.warning('There is nothing to do')
    else:
        pipe_claims = []
        if output_file_text == '-':
            pipe_claims.append('Text')
        if output_file_geojson == '-':
            pipe_claims.append('GeoJSON')
        if output_file_kml == '-':
            pipe_claims.append('KML')
        if output_file_csv == '-':
            pipe_claims.append('CSV')
        if len(pipe_claims) > 1:
            log.warning('More than one format specified for printing. You probably want to disable one of the following: {}'
                        .format(', '.join(pipe_claims)))

        users = get_users(url=input_url, local=input_file)
        if users is None:
            return None
        parsed_users = parse_users(users)

        if output_file_text not in dont_run:
            make_text(parsed_users, output_file_text, pretty=pretty)
        if output_file_geojson not in dont_run:
            make_geojson(parsed_users, output_file_geojson)
        if output_file_kml not in dont_run:
            make_kml(parsed_users, output_file_kml)
        if output_file_csv not in dont_run:
            make_csv(parsed_users, output_file_csv)


# If the script is being run and not imported...
if __name__ == '__main__':
    main()
