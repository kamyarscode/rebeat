import requests
from helpers import with_auth_headers


def get_recently_played_using_time(after):

    # Get time from source ie Strava. Leave now for testing.
    # after = datetime_to_iso_test()
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
    SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played"

    # TODO: Add docs here to explain "after" later
    params = {
        "after": after,
    }

    # Make API request to Spotify here.
    response = requests.get(
        SPOTIFY_RECENTLY_PLAYED_URL, headers=with_auth_headers(), params=params
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.json())

    # Get response object.
    response_json = response.json()

    # Map function to get track names from response.
    recently_played_song_names = list(
        map(lambda x: x["track"]["name"], response_json["items"])
    )
    recently_played_song_id = list(
        map(lambda x: x["track"]["id"], response_json["items"])
    )

    # Return list of song names for testing, return id for actual use.
    return recently_played_song_names, recently_played_song_id
