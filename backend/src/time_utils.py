from dateutil import parser
from datetime import timezone


def iso_to_unix(iso_string: str) -> int:
    """Convert an ISO 8601 string to a Unix timestamp in milliseconds.

    Milliseconds, not seconds: that is what Spotify's cursor parameters expect.

    Args:
        iso_string: The ISO 8601 formatted string. Naive values are read as UTC.

    Returns:
        Milliseconds since the epoch.
    """
    dt = parser.isoparse(iso_string)  # preserves tz if present
    if dt.tzinfo is None:  # assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)
