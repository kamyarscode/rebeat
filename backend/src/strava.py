from datetime import datetime, timezone, timedelta
import os
from urllib.parse import urlencode
from src.db_ops import store_token
from src.strava_models import RefreshStravaAccessTokenResponse, StravaAuthResponse
from src.helpers import build_state
from dotenv import load_dotenv
from requests import post, get, put
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.db import Token
from time_utils import iso_to_unix
from spotify import build_playlist

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_SCOPE = "activity:read_all,activity:write"

STRAVA_REDIRECT_URI = f"{BASE_URL}/api/strava/callback"
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_ACCESS_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"


def build_strava_auth_url(token: str):
    # Generate a state parameter to include the JWT token
    state = build_state(token=token)

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": STRAVA_SCOPE,
        "state": state,
    }
    return f"{STRAVA_AUTH_URL}?{urlencode(params)}"


def exchange_strava_code_for_access_token(code: str):
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = post(STRAVA_ACCESS_TOKEN_URL, data=params).json()
    return StravaAuthResponse.model_validate(response)


def refresh_strava_access_token(
    token: Token, db: Session
) -> RefreshStravaAccessTokenResponse:
    body = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
    }
    response = post(STRAVA_ACCESS_TOKEN_URL, data=body)
    if response.status_code != 200:
        raise Exception(f"Failed to refresh Strava access token: {response.json()}")
    response_json = response.json()
    if response_json.get("error"):
        raise Exception(
            f"Failed to refresh Strava access token: {response_json['error']}"
        )
    object: RefreshStravaAccessTokenResponse = (
        RefreshStravaAccessTokenResponse.model_validate(response_json)
    )
    store_token(
        db=db,
        user_id=token.user_id,
        provider="strava",
        access_token=object.access_token,
        refresh_token=object.refresh_token,
        expires_at=datetime.fromtimestamp(object.expires_at),
    )
    return object


def get_strava_access_token_from_db(user_id: int, db: Session):
    token = (
        db.query(Token)
        .filter(Token.user_id == user_id, Token.provider == "strava")
        .first()
    )
    if token.expires_at.timestamp() < datetime.now().timestamp():
        token = refresh_strava_access_token(token, db)
    return token.access_token


def compose_description(existing: str | None, playlist_url: str) -> str:
    """Append the playlist link to an activity description.

    Strava's description is nullable, so guard against writing a literal "None"
    or a pair of leading blank lines onto an activity that had no description.
    """
    existing = (existing or "").rstrip()
    return f"{existing}\n\n{playlist_url}" if existing else playlist_url


def get_latest_run(user_id: int, db: Session):
    access_token = get_strava_access_token_from_db(user_id, db)
    query_params = {
        "per_page": 1,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = get(
        f"{STRAVA_API_URL}/athlete/activities",
        params=query_params,
        headers=headers,
    )

    # Check before indexing: on a non-200 the body is an error object, and
    # response[0] would raise KeyError: 0 rather than saying what went wrong.
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Strava returned {response.status_code} when listing your activities.",
        )

    activities = response.json()
    if not activities:
        raise HTTPException(
            status_code=404,
            detail="You don't have any Strava activities yet. Record one and try again.",
        )

    id = activities[0]["id"]
    full_activity_url = f"{STRAVA_API_URL}/activities/{id}"
    activity_detail = get(full_activity_url, headers=headers)
    if activity_detail.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Strava returned {activity_detail.status_code} when fetching your latest activity.",
        )
    activity_response = activity_detail.json()
    return {
        "id": activity_response["id"],
        "name": activity_response["name"],
        "distance": activity_response["distance"],
        "moving_time": activity_response["moving_time"],
        "start_date": activity_response["start_date"],
        "elapsed_time": activity_response["elapsed_time"],
        "description": activity_response["description"],
        "url": f"https://www.strava.com/activities/{activity_response['id']}",
    }


def add_playlist_to_latest_run(user_id: int, spotify_user_id: str, db: Session):
    latest_run = get_latest_run(user_id, db)
    latest_run_id = latest_run["id"]
    latest_run_description = latest_run["description"]

    # Parse start (robust to 'Z')
    start_dt_utc = datetime.fromisoformat(
        latest_run["start_date"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)
    end_dt_utc = start_dt_utc + timedelta(seconds=latest_run["elapsed_time"])
    start_time_iso_utc = start_dt_utc.isoformat().replace("+00:00", "Z")
    end_time_iso_utc = end_dt_utc.isoformat().replace("+00:00", "Z")

    playlist_url = build_playlist(
        user_id=user_id,
        spotify_user_id=spotify_user_id,
        start_time=start_time_iso_utc,
        end_time=end_time_iso_utc,
        playlist_name=latest_run["name"],
        playlist_description=f"The songs played during a run called {latest_run['name']}",
        db=db,
    )

    access_token = get_strava_access_token_from_db(user_id, db)
    body = {
        "description": compose_description(latest_run_description, playlist_url),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = put(
        f"{STRAVA_API_URL}/activities/{latest_run_id}",
        data=body,
        headers=headers,
    ).json()
    return response
