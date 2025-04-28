"""
Get the time stamps and convert to standard way for ingestion.
"""

import time
from dateutil import parser


def iso_to_unix(iso_string):
    """Converts an ISO 8601 formatted string to a Unix timestamp (seconds since epoch).

    Args:
        iso_string: The ISO 8601 formatted string.

    Returns:
        The Unix timestamp as a float.
    """
    dt_object = parser.parse(iso_string)
    timestamp = time.mktime(dt_object.timetuple())
    return timestamp


# Time comes in from Strava.
def get_time():
    pass


# comes in in minutes
# convert to A Unix timestamp in milliseconds for spotify.
def normalize_time(start, end):

    normalized = map(lambda x: x * 1000 * 60, [start, end])
    return list(normalized)
