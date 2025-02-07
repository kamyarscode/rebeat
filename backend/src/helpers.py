import datetime
import math
import os
from normalize_time import iso_to_unix
from dotenv import load_dotenv

load_dotenv()

# Set up test for passing input from Strava for now.
def datetime_to_iso_test():

    # Get the current time as datetime object.
    current_time = datetime.datetime.now()
    # Calculate time 5 minutes ago, reeturns datetime object.
    test_five_min_ago = (current_time - datetime.timedelta(minutes=10))

    # Convert 5 minutes ago to ISO 8601 format (Strava format).
    iso_string = test_five_min_ago.isoformat()

    # Convert to Unix timestamp in milliseconds (What Spotify wants).
    unix_milliseconds = iso_to_unix(iso_string) * 1000

    # Truncate and get rid of decimal points.
    after = math.trunc(unix_milliseconds)

    # Return truncated epoch time in milliseconds.
    return after


# Set up auth headers for base and whatever else is needed. 
def with_auth_headers(headers: dict = {}) -> dict:
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    auth_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    return {**headers, **auth_headers}

