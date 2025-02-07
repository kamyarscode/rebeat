import requests
from helpers import datetime_to_iso_test, with_auth_headers


def get_recently_played_using_time(after):

    # Get time from source ie Strava. Leave now for testing.
    #after = datetime_to_iso_test()

    SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played"

    # TODO: Add docs here to explain "after" later
    params = {
        "after": after,

    }

    # Make API request to Spotify here.
    response = requests.get(SPOTIFY_RECENTLY_PLAYED_URL, headers=with_auth_headers(), params=params)
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.json())
    
    # Get response object.
    response_json = response.json()
    
    # Map function to get track names from response.
    recently_played_song_names = map(lambda x: x['track']['name'], response_json['items'])

    # Return list of song names.
    return recently_played_song_names

