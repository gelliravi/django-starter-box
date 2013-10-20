from __future__ import unicode_literals

import dateutil.parser

def parse_iso_datetime(str):
    """
    Parses an ISO-formatted datetime string in any time zone
    and returns in UTC timezone.

    :param  str:    Example, '2013-03-01T01:01:01Z'
    """

    return dateutil.parser.parse(str).astimezone(dateutil.tz.tzutc())
