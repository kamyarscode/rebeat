import requests
from helpers import with_auth_headers
import json
import pprint
from datetime import date, datetime
from time_utils import iso_to_unix
from  typing import List

"""
Get recently played songs.
GET https://api.spotify.com/v1/me/player/recently-played

Parameters/Args:
    limit: int - The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.

    after: int - A Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position.
                If after is specified, before must not be specified.
                Example: after=1484811043508

    before: int - A Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position.
                If before is specified, after must not be specified.

Returns:
    list: A list of song names.

"""
def get_recently_played_using_time(before: str, start_time: str) -> List[str]:

    SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played"
    recently_played_song_names = []
    recently_played_song_id = []
    # TODO: Add docs here to explain "before" later
    params = {
        "before": before
    }

    # Make API request to Spotify here.
    response = requests.get(
        SPOTIFY_RECENTLY_PLAYED_URL, headers=with_auth_headers(), params=params
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.json())

    # Get response object.
    response_json = response.json()
  
    for item in response_json["items"]:
        # convert both times to format for comparison. 
        played_at_unix_milliseconds = iso_to_unix(item["played_at"])
        start_time_unix_milliseconds = iso_to_unix(start_time)

        # logic to check if song played is after start time.
        if played_at_unix_milliseconds > start_time_unix_milliseconds:
            recently_played_song_id.append(item["track"]["id"])
            recently_played_song_names.append(item["track"]["name"])


    # Return list of song names for testing, return id for actual use.
    return recently_played_song_id

### Rough logic:

"""
Get all songs before the end of activity. i.e finish activity at 5:30, get all songs before 5:30.
Check played_at time for each song. 
If played_at is greater than the after parameter, don't add to playlist. 

"""