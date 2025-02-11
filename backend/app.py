from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, Query
from src.strava_interface import subscribe_to_strava
import uvicorn
from helpers import generate_random_string
from urllib.parse import urlencode
import os
import base64
from requests import post

app = FastAPI()


VERIFICATION_TOKEN = "placeholder"

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

    return {"message": "Login reached"}

# Strava GET request to verify the callback URL.
@app.get("/strava/webhook")
def verify_webhook( hub_mode: str = Query(...), hub_challenge: str = Query(...), hub_verify_token: str = Query(...)):
    """
    Strava will send a GET request to verify the callback URL.
    Check if tokens match and respond back with hub.challenge.
    
    Args:
        hub_mode: str - Strava hub.mode.
        hub_challenge: str - Strava hub.challenge.
        hub_verify_token: str - Strava hub.verify_token.

    Returns:
        dict: hub.challenge if tokens match, error message otherwise.
    """
    if hub_mode != "subscribe":
        return {"error": "Invalid hub.mode"}
    
    if hub_verify_token == VERIFICATION_TOKEN:
        return {"hub.challenge": hub_challenge}
    
    return {"error": "Invalid verification token"}

# Strava POST request to receive activity updates.
@app.post("/strava/webhook")
async def receive_strava_updates(request: Request):
    """
    Receive activity updates from Strava.

    Args:   
        request: Request - FastAPI request object.

    Returns:
        dict: Status message.
    """
    payload = await request.json()
    print("Received Strava update:", payload)  # See the update for now.

    return {"status": "Received"}

# Connect to Strava endpoint, kick things off with subscribe_to_strava.
@app.get("/strava/connect")
def connect_to_strava():
    """
    Trigger the Strava subscription process when a user visits this endpoint.
    """
    subscribe_to_strava(CLIENT_ID="", CLIENT_SECRET="", CALLBACK_URL="", VERIFICATION_TOKEN=VERIFICATION_TOKEN) 
    return {"message": "Subscription request sent to Strava"}


# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
