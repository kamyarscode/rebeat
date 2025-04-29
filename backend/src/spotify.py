from helpers import generate_random_string
from urllib.parse import urlencode
import os
import base64
import json
from requests import post
from dotenv import load_dotenv

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

    # Generate a random state for CSRF protection
    random_state = generate_random_string(16)

    # If a token is provided, include it in the state
    if token:
        # Create a state object with both the random state and the token
        state_obj = {"random": random_state, "token": token}
        # Encode it as JSON, then base64 to make it URL-safe
        state = base64.b64encode(json.dumps(state_obj).encode()).decode()
    else:
        state = random_state

    scope = "user-read-private user-read-email playlist-modify-private user-read-recently-played"
    params = {
        "response_type": "code",
        "client_id": spotify_client_id,
        "scope": scope,
        "redirect_uri": spotify_redirect_uri,
        "state": state,
    }

    return f"{url}?{urlencode(params)}"


# Helper to decode the state parameter that might contain a token
def decode_state(state_param):
    try:
        # Try to decode as base64 and JSON
        decoded_bytes = base64.b64decode(state_param)
        state_obj = json.loads(decoded_bytes)
        return state_obj
    except:
        # If decoding fails, it's just a simple state string
        return {"random": state_param}
