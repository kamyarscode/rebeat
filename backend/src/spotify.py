from urllib.parse import urlencode
import os
import base64
import requests
from db_ops import store_token
from spotify_models import RefreshSpotifyAccessTokenResponse
from dotenv import load_dotenv
from src.helpers import build_state
from sqlalchemy.orm import Session
from src.db import Token
from time_utils import iso_to_unix
from listening_history import (
    HISTORY_CAPACITY,
    Status,
    select_tracks_in_window,
)
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

load_dotenv()

base_url = os.getenv("BASE_URL")

spotify_client_id = os.getenv("CLIENT_ID")
spotify_client_secret = os.getenv("CLIENT_SECRET")
spotify_redirect_uri = f"{base_url}/api/spotify/callback"
SPOTIFY_ACCESS_TOKEN_URL = "https://accounts.spotify.com/api/token"


def build_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def _format_horizon(horizon_ms: int) -> str:
    """Render the history horizon for a user-facing message."""
    return (
        datetime.fromtimestamp(horizon_ms / 1000, timezone.utc)
        .strftime("%b %-d at %H:%M UTC")
    )


# Helper to exchange the code for an access token via spotify's API
def exchange_code_for_access_token(code: str) -> str:
    base64_encoded_client_id_and_secret = base64.b64encode(
        f"{spotify_client_id}:{spotify_client_secret}".encode()
    ).decode()

    form = {
        "code": code,
        "redirect_uri": spotify_redirect_uri,
        "grant_type": "authorization_code",
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64_encoded_client_id_and_secret}",
    }
    response = requests.post(SPOTIFY_ACCESS_TOKEN_URL, data=form, headers=headers)
    return response.json()


def build_spotify_login_url(token=None):
    url = "https://accounts.spotify.com/authorize"

    state = build_state(token)

    scope = "user-read-private user-read-email playlist-modify-private playlist-modify-public user-read-recently-played"
    params = {
        "response_type": "code",
        "client_id": spotify_client_id,
        "scope": scope,
        "redirect_uri": spotify_redirect_uri,
        "state": state,
    }

    return f"{url}?{urlencode(params)}"


# TODO: probably combine this with exchange_code_for_access_token
def refresh_spotify_access_token(
    token: Token, db: Session
) -> RefreshSpotifyAccessTokenResponse:
    base64_encoded_client_id_and_secret = base64.b64encode(
        f"{spotify_client_id}:{spotify_client_secret}".encode()
    ).decode()

    body = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
    }
    response = requests.post(
        SPOTIFY_ACCESS_TOKEN_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64_encoded_client_id_and_secret}",
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh Spotify access token: {response.json()}")
    response_json = response.json()
    if response_json.get("error"):
        raise Exception(
            f"Failed to refresh Spotify access token: {response_json['error']}"
        )
    object: RefreshSpotifyAccessTokenResponse = (
        RefreshSpotifyAccessTokenResponse.model_validate(response_json)
    )

    expires_at = datetime.now() + timedelta(seconds=object.expires_in)

    store_token(
        db=db,
        user_id=token.user_id,
        provider="spotify",
        access_token=object.access_token,
        refresh_token=object.refresh_token or token.refresh_token,
        expires_at=expires_at,
    )
    return object


def get_spotify_access_token_from_db(user_id: int, db: Session):
    token = (
        db.query(Token)
        .filter(Token.user_id == user_id, Token.provider == "spotify")
        .first()
    )
    if token.expires_at.timestamp() < datetime.now().timestamp():
        token = refresh_spotify_access_token(token, db)
    return token.access_token


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
    user_id: str,
    token: str,
    playlist_name: str,
    playlist_description: str,
    public: bool,
) -> str:
    SPOTIFY_CREATE_PLAYLIST_URL = "https://api.spotify.com/v1/users/{user_id}/playlists"
    data = {
        "name": playlist_name,
        "description": playlist_description,
        "public": public,
    }

    try:
        response = requests.post(
            SPOTIFY_CREATE_PLAYLIST_URL.format(user_id=user_id),
            headers=build_headers(token),
            json=data,
        )
        response.raise_for_status()

        # Return ID of playlist for now.
        return response.json()["id"]

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


"""
Reference:
GET https://api.spotify.com/v1/playlists/{playlist_id}
POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
"""


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


def get_recently_played(token: str) -> list:
    """Fetch the whole recently-played buffer, newest first.

    No `before`/`after` cursor: the buffer only ever holds HISTORY_CAPACITY
    items and the cursors cannot page outside it, so asking for all of it and
    filtering locally is both simpler and strictly more informative -- it gives
    us the horizon for free. Note that the response's `next` field is non-null
    even when following it yields nothing, so it is not a usable signal.
    """
    SPOTIFY_RECENTLY_PLAYED_URL = "https://api.spotify.com/v1/me/player/recently-played"

    response = requests.get(
        SPOTIFY_RECENTLY_PLAYED_URL,
        headers=build_headers(token),
        params={"limit": HISTORY_CAPACITY},
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.json())

    return response.json()["items"]


def add_songs(
    recently_played_songs_id_array: list, playlist_id: str, token: str
) -> dict:
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
            headers=build_headers(token),
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


def build_playlist(
    user_id: str,
    spotify_user_id: str,
    start_time: str,
    end_time: str,
    db: Session,
    playlist_name="Songs from your run",
    playlist_description="Songs listened to during your run",
    public=True,
    include_protocol=True,
) -> str:
    # Set up the base URL for Spotify web playlists
    SPOTIFY_WEB_URL_BASE = (
        "https://open.spotify.com/playlist/"
        if include_protocol
        else "open.spotify.com/playlist/"
    )

    token = get_spotify_access_token_from_db(user_id, db)

    # Pull the whole history buffer and work out what it can tell us about this
    # particular run. Distinct statuses matter here: "you played nothing" and
    # "we can no longer see that far back" are very different messages.
    selection = select_tracks_in_window(
        items=get_recently_played(token),
        start_ms=iso_to_unix(start_time),
        end_ms=iso_to_unix(end_time),
    )
    print(f"{selection.status.value}: {len(selection.track_ids)} tracks", flush=True)

    if selection.status is Status.HORIZON_EXCEEDED:
        raise HTTPException(
            status_code=410,
            detail=(
                f"This run is older than your Spotify listening history, which only "
                f"reaches back to {_format_horizon(selection.horizon_ms)}. Spotify "
                f"keeps just your last {HISTORY_CAPACITY} tracks, so we can't tell "
                f"what you were playing during this run."
            ),
        )

    if not selection.is_playable:
        raise HTTPException(
            status_code=400,
            detail=(
                "No songs were played during this run. Make sure you were listening "
                "to music on Spotify during your activity."
            ),
        )

    song_ids = selection.track_ids

    # Say so rather than quietly handing over a playlist that is missing the
    # start of the run.
    if selection.status is Status.PARTIAL:
        playlist_description += (
            " (Partial: Spotify had already dropped the earliest tracks of this run"
            " from your listening history.)"
        )

    # Create a new playlist with the provided details
    playlist_id = create_playlist(
        user_id=spotify_user_id,
        playlist_name=playlist_name,
        playlist_description=playlist_description,
        public=public,
        token=token,
    )

    # Add the recently played songs to the created playlist
    add_songs(
        recently_played_songs_id_array=list(song_ids),
        playlist_id=playlist_id,
        token=token,
    )
    print(playlist_id, flush=True)

    # Return the Spotify web URL for the created playlist
    return SPOTIFY_WEB_URL_BASE + playlist_id
