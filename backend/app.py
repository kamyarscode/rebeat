from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn
from helpers import generate_random_string
from urllib.parse import urlencode
import os
import base64
from requests import post

app = FastAPI()


# Root route
@app.get("/")
async def root():

    return {"message": "Welcome to Rebeat"}


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8000/callback"


# Helper to exchange the code for an access token via spotify's API
def exchange_code_for_access_token(code: str) -> str:
    url = "https://accounts.spotify.com/api/token"
    base64_encoded_client_id_and_secret = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    form = {
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64_encoded_client_id_and_secret}",
    }
    response = post(url, data=form, headers=headers)
    return response.json()


# Begins the authorization process. Redirects to spotify's authorization page for user consent.
# More info at: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
@app.get("/login")
def login():
    url = "https://accounts.spotify.com/authorize"

    # TODO: Store state and compare to the state in the callback.
    state = generate_random_string(16)
    scope = "user-read-private user-read-email playlist-modify-private user-read-recently-played"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
    }

    return RedirectResponse(f"{url}?{urlencode(params)}")


# Receives the code and state from spotify, and then exchanges the code for an access token
@app.get("/callback")
async def callback(request: Request):
    # TODO: Store state and compare to the state here.
    code: str | None = request.query_params.get("code")
    state: str | None = request.query_params.get("state")
    error: str | None = request.query_params.get("error")

    # If there is an error, redirect to the frontend with the error.
    if error:
        return RedirectResponse(url=os.getenv("FRONTEND_URL") + "/error?error=" + error)

    # If there is no state, redirect to the frontend with an error.
    if not state:
        return RedirectResponse(url=os.getenv("FRONTEND_URL") + "/error?error=no_state")

    # If there is no code, redirect to the frontend with an error.
    if not code:
        return RedirectResponse(url=os.getenv("FRONTEND_URL") + "/error?error=no_code")

    token_response = exchange_code_for_access_token(code)
    print(token_response)

    # TODO: Store the access token in the database associated with a user.
    # For now, just redirect to the frontend with the access token. (bad)
    return RedirectResponse(
        url=os.getenv("FRONTEND_URL")
        + "?access_token="
        + token_response["access_token"]
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
