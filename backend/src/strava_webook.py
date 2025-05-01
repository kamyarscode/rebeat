import requests


def subscribe_to_strava(
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, CALLBACK_URL, VERIFICATION_TOKEN
):
    """
    Function to create a subscription with Strava.

    Args:
        CLIENT_ID: str - Strava client ID.
        CLIENT_SECRET: str - Strava client secret.
        CALLBACK_URL: str - URL where Strava will send updates.
        VERIFICATION_TOKEN: str - Token to verify the subscription.

    Returns:
        None - prints success message if subscription is successful.
    """
    STRAVA_SUBSCRIPTION_URL = "https://www.strava.com/api/v3/push_subscriptions"

    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "callback_url": CALLBACK_URL,
        "verify_token": VERIFICATION_TOKEN,
    }

    response = requests.post(STRAVA_SUBSCRIPTION_URL, json=data)

    if response.status_code == 201:
        print("Successfully subscribed to Strava updates")
    else:
        print("Failed to subscribe:", response.json())

    return response.json()


# See below for how to call the above function at the server root and respond to its redirect.

# STRAVA_SUB_CALLBACK_URL = os.getenv("STRAVA_CALLBACK_URL")
# STRAVA_SUB_VERIFICATION_TOKEN = generate_random_string(16)

# @app.get("/strava/webhook")
# def verify_webhook(request: Request):

#     hub_mode = request.query_params.get("hub.mode")
#     hub_challenge = request.query_params.get("hub.challenge")
#     hub_verify_token = request.query_params.get("hub.verify_token")

#     print(hub_mode, hub_challenge, hub_verify_token)

#     """
#     Strava will send a GET request to verify the callback URL.
#     Check if tokens match and respond back with hub.challenge.

#     Args:
#         hub_mode: str - Strava hub.mode.
#         hub_challenge: str - Strava hub.challenge.
#         hub_verify_token: str - Strava hub.verify_token.

#     Returns:
#         dict: hub.challenge if tokens match, error message otherwise.
#     """
#     if hub_mode != "subscribe":
#         return {"error": "Invalid hub.mode"}

#     if hub_verify_token == STRAVA_SUB_VERIFICATION_TOKEN:
#         return {"hub.challenge": hub_challenge}

#     return {"error": "Invalid verification token"}


# # NOT WORKING, INCOMPLETE: Connect to Strava endpoint, kick things off with subscribe_to_strava.
# @app.get("/strava/subscribe")
# def connect_to_strava():
#     """
#     Trigger the Strava subscription process when a user visits this endpoint.
#     """

#     subscribe_to_strava(
#         STRAVA_CLIENT_ID=STRAVA_CLIENT_ID,
#         STRAVA_CLIENT_SECRET=STRAVA_CLIENT_SECRET,
#         CALLBACK_URL=STRAVA_SUB_CALLBACK_URL,
#         VERIFICATION_TOKEN=STRAVA_SUB_VERIFICATION_TOKEN,
#     )

#     return {"message": "Subscription request sent to Strava"}
