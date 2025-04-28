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
