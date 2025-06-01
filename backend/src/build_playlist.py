from helpers import with_auth_headers
from get_songs import get_recently_played_using_time
import requests

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
def create_playlist(
    user_id: str, playlist_name="default playlist name", 
    playlist_description="default playlist description",
    public=True) -> dict:


    SPOTIFY_CREATE_PLAYLIST_URL = "https://api.spotify.com/v1/users/{user_id}/playlists"
    data = {
        "name": playlist_name,
        "description": playlist_description,
        "public": public,
    }

    try:
        response = requests.post(
            SPOTIFY_CREATE_PLAYLIST_URL.format(user_id=user_id),
            headers=with_auth_headers(),
            json=data,
        )
        response.raise_for_status()

        # Return ID of playlist for now.
        return response.json()["id"]

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def add_songs(recently_played_songs_id_array: list, playlist_id: str) -> dict:
    """
    Reference:
    GET https://api.spotify.com/v1/playlists/{playlist_id}
    POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    """
    SPOTIFY_ADD_TO_PLAYLIST_URL = (
        "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    )

    data = {
        "uris": [f"spotify:track:{x}" for x in recently_played_songs_id_array],
        "position": 0,
    }

    try:
        response = requests.post(
            SPOTIFY_ADD_TO_PLAYLIST_URL.format(playlist_id=playlist_id),
            headers=with_auth_headers(),
            json=data,
        )
        response.raise_for_status()

        # Return response object
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

"""
Function to build a Spotify playlist after an activity based on the user's recently played songs.

Parameters:
    user_id (str): The Spotify user ID.
    playlist_name (str): The name of the playlist to be created.
    playlist_description (str): The description of the playlist.
    public (bool): Whether the playlist should be public or private.
    start_time (str): The start time of the activity in ISO 8601 format.
    end_time (str): The end time of the activity in ISO 8601 format.

Returns:
    str: The Spotify web URL of the created playlist.

"""
def build_playlist_after_activity(user_id: str,
                                start_time: str, 
                                end_time: str, 
                                playlist_name="default playlist name", 
                                playlist_description="default playlist description",
                                public=True, ) -> str:
    
    # Set up the base URL for Spotify web playlists
    SPOTIFY_WEB_URL_BASE = "https://open.spotify.com/playlist/"
    
    # Get the recently played songs using the provided time range
    song_ids = get_recently_played_using_time(before=end_time, start_time=start_time)

    # Create a new playlist with the provided details
    playlist_id = create_playlist(
        user_id=user_id,
    )

    # Add the recently played songs to the created playlist
    add_songs(
    recently_played_songs_id_array=list(song_ids), playlist_id=playlist_id
    )

    # Return the Spotify web URL for the created playlist
    return SPOTIFY_WEB_URL_BASE + playlist_id
