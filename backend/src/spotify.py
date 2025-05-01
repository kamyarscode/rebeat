from helpers import generate_random_string
from urllib.parse import urlencode
import os
import base64
from requests import post
from dotenv import load_dotenv
from src.helpers import build_state

load_dotenv()


base_url = os.getenv("BASE_URL")

spotify_client_id = os.getenv("CLIENT_ID")
spotify_client_secret = os.getenv("CLIENT_SECRET")
spotify_redirect_uri = f"{base_url}/spotify/callback"


# Helper to exchange the code for an access token via spotify's API
def exchange_code_for_access_token(code: str) -> str:
    url = "https://accounts.spotify.com/api/token"
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
    response = post(url, data=form, headers=headers)
    return response.json()


def build_spotify_login_url(token=None):
    url = "https://accounts.spotify.com/authorize"

    state = build_state(token)

    scope = "user-read-private user-read-email playlist-modify-private user-read-recently-played"
    params = {
        "response_type": "code",
        "client_id": spotify_client_id,
        "scope": scope,
        "redirect_uri": spotify_redirect_uri,
        "state": state,
    }

    return f"{url}?{urlencode(params)}"
