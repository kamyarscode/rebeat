from dateutil import parser
import math
from datetime import datetime, timezone


"""Converts an ISO 8601 formatted string to a Unix timestamp (milliseconds since epoch).

Args:
    iso_string: The ISO 8601 formatted string.

Returns:
    The Unix timestamp as a float.
"""


def iso_to_unix(iso_string: str) -> int:
    dt = parser.isoparse(iso_string)  # preserves tz if present
    if dt.tzinfo is None:  # assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


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
    # Get the current time as datetime object to conver later.
    end_time = datetime.datetime.utcnow()

    # Calculate time 20 minutes ago, returns datetime object.
    start_time = end_time - datetime.timedelta(minutes=15)

    # Convert 5 minutes ago to ISO 8601 format (Strava format).
    start_iso_string = start_time.isoformat()
    end_iso_string = end_time.isoformat()

    # Convert to Unix timestamp in milliseconds (What Spotify wants).
    start_unix_milliseconds = iso_to_unix(start_iso_string) * 1000
    end_unix_milliseconds = iso_to_unix(end_iso_string) * 1000

    # Truncate and get rid of decimal points.
    start_time = math.trunc(start_unix_milliseconds)
    end_time = math.trunc(end_unix_milliseconds)

    # remove decimal from iso start time iso string.
    truncated_start_time_iso = start_iso_string.split(".")[0] + "Z"

    # Return truncated epoch time in milliseconds.
    return truncated_start_time_iso, end_time


# Compare two dates in ISO 8601 format and return True if the first date is before the second date.
def compare_dates():
    pass
