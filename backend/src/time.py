import time
from dateutil import parser
import math
import datetime


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


# Set up test for passing input from Strava for now.
def datetime_to_iso_test():

    # Get the current time as datetime object.
    current_time = datetime.datetime.now()
    # Calculate time 5 minutes ago, reeturns datetime object.
    test_five_min_ago = current_time - datetime.timedelta(minutes=10)

    # Convert 5 minutes ago to ISO 8601 format (Strava format).
    iso_string = test_five_min_ago.isoformat()

    # Convert to Unix timestamp in milliseconds (What Spotify wants).
    unix_milliseconds = iso_to_unix(iso_string) * 1000

    # Truncate and get rid of decimal points.
    after = math.trunc(unix_milliseconds)

    # Return truncated epoch time in milliseconds.
    return after
