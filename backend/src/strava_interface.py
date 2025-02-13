import requests

def subscribe_to_strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, CALLBACK_URL, VERIFICATION_TOKEN):
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
        "verify_token": VERIFICATION_TOKEN
    }

    response = requests.post(STRAVA_SUBSCRIPTION_URL, json=data)
    
    if response.status_code == 201:
        print("Successfully subscribed to Strava updates")
    else:
        print("Failed to subscribe:", response.json())

    return response.json()

