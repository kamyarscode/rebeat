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
        str: ID of the playlist.

    """

    SPOTIFY_CREATE_PLAYLIST_URL = "https://api.spotify.com/v1/users/{user_id}/playlists"
    data = {
    "name": playlist_name,
    "description": playlist_description,
    "public": public
    }

    try:
        response = requests.post(SPOTIFY_CREATE_PLAYLIST_URL.format(user_id=user_id), headers=with_auth_headers(), json=data)
        response.raise_for_status()

        # Return ID of playlist for now.
        return response.json()['id']
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def add_songs(recently_played_songs_id_array: list, playlist_id: str) -> dict:
    """
    Reference:
    GET https://api.spotify.com/v1/playlists/{playlist_id}
    POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    """
    SPOTIFY_ADD_TO_PLAYLIST_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    data = {
    "uris": [f"spotify:track:{x}" for x in recently_played_songs_id_array],
    "position": 0
    }

    try:
        response = requests.post(SPOTIFY_ADD_TO_PLAYLIST_URL.format(playlist_id=playlist_id), headers=with_auth_headers(), json=data)
        response.raise_for_status()

        # Return response object
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    