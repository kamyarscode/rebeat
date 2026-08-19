"""Tests for run-window track selection.

The interesting behaviour is the distinction between "you played nothing during
this run" and "we can no longer see far enough back to know", so most of these
cases are about that boundary.

Buffer shapes here mirror what Spotify actually returns: newest item first,
at most HISTORY_CAPACITY items.
"""

import pytest

from listening_history import (
    HISTORY_CAPACITY,
    DEFAULT_PAD_MS,
    Status,
    select_tracks_in_window,
)
from time_utils import iso_to_unix


def play(iso: str, track_id: str) -> dict:
    return {"played_at": iso, "track": {"id": track_id}}


def buffer_of(count: int, oldest_iso: str = "2026-08-18T16:47:43.366Z") -> list:
    """A newest-first buffer of `count` plays, one minute apart."""
    base = iso_to_unix(oldest_iso)
    items = [
        play(_iso(base + i * 60_000), f"track-{i}")
        for i in range(count)
    ]
    return list(reversed(items))


def _iso(ms: int) -> str:
    from datetime import datetime, timezone

    return (
        datetime.fromtimestamp(ms / 1000, timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


RUN_START = "2026-08-19T06:00:00Z"
RUN_END = "2026-08-19T06:45:00Z"


def select(items, start=RUN_START, end=RUN_END, **kwargs):
    return select_tracks_in_window(items, iso_to_unix(start), iso_to_unix(end), **kwargs)


def test_tracks_within_the_window_are_selected():
    items = [
        play("2026-08-19T06:30:00Z", "during-2"),
        play("2026-08-19T06:10:00Z", "during-1"),
    ]
    result = select(items)
    assert result.status is Status.OK
    assert result.track_ids == ["during-1", "during-2"]


def test_tracks_outside_the_window_are_excluded_on_both_sides():
    """The old implementation had no upper bound, so post-run plays leaked in."""
    items = [
        play("2026-08-19T09:00:00Z", "after-run"),
        play("2026-08-19T06:20:00Z", "during"),
        play("2026-08-19T01:00:00Z", "before-run"),
    ]
    result = select(items)
    assert result.track_ids == ["during"]


def test_tracks_are_returned_oldest_first():
    """So the playlist reads in the order the run was run."""
    items = [
        play("2026-08-19T06:40:00Z", "third"),
        play("2026-08-19T06:20:00Z", "second"),
        play("2026-08-19T06:05:00Z", "first"),
    ]
    assert select(items).track_ids == ["first", "second", "third"]


def test_empty_buffer_reports_no_history():
    result = select([])
    assert result.status is Status.NO_HISTORY
    assert result.horizon_ms is None


def test_full_buffer_newer_than_the_run_refuses_to_guess():
    """The run predates everything we can see, so a miss is not informative."""
    items = buffer_of(HISTORY_CAPACITY, oldest_iso="2026-08-19T10:00:00Z")
    result = select(items, start="2026-08-17T09:00:00Z", end="2026-08-17T10:00:00Z")
    assert result.status is Status.HORIZON_EXCEEDED
    assert result.track_ids == []
    assert result.horizon_ms == iso_to_unix("2026-08-19T10:00:00Z")


def test_partial_buffer_newer_than_the_run_is_a_genuine_miss():
    """Nothing was evicted, so the absence of tracks is trustworthy.

    This is the case that separates the two failure modes: same run, same
    horizon, different verdict purely because the buffer was not full.
    """
    items = buffer_of(HISTORY_CAPACITY - 1, oldest_iso="2026-08-19T10:00:00Z")
    result = select(items, start="2026-08-17T09:00:00Z", end="2026-08-17T10:00:00Z")
    assert result.status is Status.NO_SONGS_PLAYED
    assert result.track_ids == []


def test_run_straddling_the_horizon_is_partial():
    """We found something, but the opening of the run is already gone."""
    horizon = "2026-08-19T06:20:00Z"
    items = buffer_of(HISTORY_CAPACITY, oldest_iso=horizon)
    result = select(items, start="2026-08-19T06:00:00Z", end="2026-08-19T07:00:00Z")
    assert result.status is Status.PARTIAL
    assert result.track_ids


def test_silence_inside_a_covered_window_is_a_genuine_miss():
    """Full buffer, but it reaches back past the run and holds nothing in it."""
    items = buffer_of(HISTORY_CAPACITY, oldest_iso="2026-08-19T08:00:00Z")
    result = select(items, start="2026-08-19T12:00:00Z", end="2026-08-19T12:30:00Z")
    assert result.status is Status.NO_SONGS_PLAYED


@pytest.mark.parametrize("offset_ms", [0, DEFAULT_PAD_MS - 1000])
def test_padding_admits_tracks_just_outside_the_window(offset_ms):
    """`played_at` may mark the start or the end of a play, so the edges are fuzzy."""
    just_before = iso_to_unix(RUN_START) - offset_ms
    items = [play(_iso(just_before), "edge")]
    assert select(items).track_ids == ["edge"]


def test_padding_does_not_admit_tracks_well_outside_the_window():
    long_before = iso_to_unix(RUN_START) - (DEFAULT_PAD_MS * 3)
    items = [play(_iso(long_before), "too-early")]
    assert select(items).track_ids == []


def test_horizon_is_the_oldest_visible_play():
    items = buffer_of(10, oldest_iso="2026-08-18T16:47:43.366Z")
    result = select(items)
    assert result.horizon_ms == iso_to_unix("2026-08-18T16:47:43.366Z")


@pytest.mark.parametrize(
    "status,playable",
    [
        (Status.OK, True),
        (Status.PARTIAL, True),
        (Status.NO_SONGS_PLAYED, False),
        (Status.HORIZON_EXCEEDED, False),
        (Status.NO_HISTORY, False),
    ],
)
def test_is_playable_covers_every_status(status, playable):
    from listening_history import Selection

    assert Selection(status=status).is_playable is playable
