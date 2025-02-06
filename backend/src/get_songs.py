import requests



def get_recently_played_using_time(AUTH_TOKEN, after):
    SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    params = {
        "after": after,

    }
    response = requests.get(SPOTIFY_RECENTLY_PLAYED_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.json())
    
    return response.json()

