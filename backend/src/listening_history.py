"""Selecting the tracks played during an activity, and knowing when we can't.

Spotify's /me/player/recently-played is a fixed-size ring buffer, not an
archive: it holds the 50 most recent plays and the 51st play evicts the oldest
permanently. Verified empirically -- paging before the oldest item returns zero
items and no cursors. For an active listener that buffer can cover as little as
half a day.

That gives us a *horizon*: the oldest play we can still see. Anything before it
is invisible, and invisible is not the same as absent. This module keeps those
two apart so callers can tell a user "you weren't listening" only when that is
actually true.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from time_utils import iso_to_unix

# Spotify retains exactly this many plays. Also the documented max for `limit`.
HISTORY_CAPACITY = 50

# `played_at` is documented only as "the date and time the track was played",
# and has been reported to mark the start of a play sometimes and the end other
# times. Rather than trust either reading, widen the window at both ends.
DEFAULT_PAD_MS = 5 * 60 * 1000


class Status(str, Enum):
    OK = "ok"
    # Some tracks found, but the run began before the horizon, so the opening
    # of the run has already been evicted. The playlist is incomplete.
    PARTIAL = "partial"
    # The buffer covers the run and holds nothing in it: a trustworthy negative.
    NO_SONGS_PLAYED = "no_songs_played"
    # The run predates the horizon. We cannot distinguish "played nothing" from
    # "played something we can no longer see", so we refuse to guess.
    HORIZON_EXCEEDED = "horizon_exceeded"
    # Spotify returned an empty buffer -- no listening history at all.
    NO_HISTORY = "no_history"


@dataclass
class Selection:
    status: Status
    track_ids: List[str] = field(default_factory=list)
    # Oldest play still visible, as Unix ms. None when the buffer is empty.
    horizon_ms: Optional[int] = None

    @property
    def is_playable(self) -> bool:
        return self.status in (Status.OK, Status.PARTIAL)


def select_tracks_in_window(
    items: list,
    start_ms: int,
    end_ms: int,
    pad_ms: int = DEFAULT_PAD_MS,
    capacity: int = HISTORY_CAPACITY,
) -> Selection:
    """Pick the tracks played during [start_ms, end_ms] and classify the result.

    `items` is the raw `items` array from recently-played, newest first. Pure --
    no network, no clock, no tokens -- so it can be tested against fixtures.
    """
    if not items:
        return Selection(status=Status.NO_HISTORY)

    plays = sorted(
        (iso_to_unix(item["played_at"]), item["track"]["id"]) for item in items
    )
    horizon_ms = plays[0][0]

    window_start = start_ms - pad_ms
    window_end = end_ms + pad_ms
    track_ids = [tid for played_at, tid in plays if window_start <= played_at <= window_end]

    # Eviction only happens once the buffer is full. If Spotify returned fewer
    # than `capacity` items then nothing has been dropped, the horizon is simply
    # the start of this user's listening, and a miss is a genuine miss.
    buffer_full = len(items) >= capacity
    lost_history = buffer_full and window_start < horizon_ms

    if track_ids:
        # Oldest first, so the playlist reads in the order the run was run.
        return Selection(
            status=Status.PARTIAL if lost_history else Status.OK,
            track_ids=track_ids,
            horizon_ms=horizon_ms,
        )

    if lost_history:
        return Selection(status=Status.HORIZON_EXCEEDED, horizon_ms=horizon_ms)

    return Selection(status=Status.NO_SONGS_PLAYED, horizon_ms=horizon_ms)
