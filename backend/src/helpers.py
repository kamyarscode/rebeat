import base64
import json
import os
import random
import string


# Set up auth headers for base and whatever else is needed.
# Make sure to call in a context where load_dotenv() has been called.
def with_auth_headers(headers: dict = {}) -> dict:
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    auth_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    return {**headers, **auth_headers}


# Generate a random string of uppercase letters and digits.
def generate_random_string(size=16) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(size))


def build_state(token=None):
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

    return state


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
