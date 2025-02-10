from helpers import with_auth_headers
import requests


def create_playlist(user_id: str, playlist_name: str, playlist_description: str, public: bool) -> dict:

    """
    Reference:
    POST https://api.spotify.com/v1/users/{user_id}/playlists

    Request body parameters
    {
      "name": "New Playlist",
      "description": "New playlist description",
      "public": false
    }

    Create a new playlist.

    Args:
        user_id: str - Spotify user ID.
        playlist_name: str - Name of the playlist.
        playlist_description: str - Description of the playlist.
        public: bool - True if playlist is public, False if private.

    Returns:
        dict: A dictionary containing the playlist details.

    """

    SPOTIFY_CREATE_PLAYLIST_URL = "https://api.spotify.com/v1/users/{user_id}/playlists"
    params = {
    "name": playlist_name,
    "description": playlist_description,
    "public": public
    }

    try:
        response = requests.post(SPOTIFY_CREATE_PLAYLIST_URL.format(user_id=user_id), headers=with_auth_headers(), json=params)
        response.raise_for_status()
        # Return ID of playlist
        return response.json()['id']
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def add_songs(recently_played_songs_array: list, playlist_id: str) -> dict:
    """
    Reference:
    GET https://api.spotify.com/v1/playlists/{playlist_id}
    POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    """


    pass