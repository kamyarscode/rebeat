"""Tests for fetching the latest activity and writing its description.

These cover the paths that used to fail confusingly: an athlete with no
activities, a non-200 from Strava, and an activity with no description.
"""

import sys
import types
from unittest import mock

import pytest


@pytest.fixture(scope="module")
def strava():
    """Import src.strava without opening a database connection.

    Only the database modules are stubbed; everything else is imported for
    real, so the test exercises the actual module graph.
    """
    for name in ("src.db", "src.db_ops", "db_ops"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["src.db"].Token = object
    sys.modules["src.db"].get_db = lambda: None
    sys.modules["src.db_ops"].store_token = lambda **kwargs: None
    sys.modules["db_ops"].store_token = lambda **kwargs: None
    import strava

    return strava


def response(status_code, payload):
    stub = mock.Mock()
    stub.status_code = status_code
    stub.json.return_value = payload
    return stub


ACTIVITY = {
    "id": 42,
    "name": "The violin",
    "distance": 5000.0,
    "moving_time": 1500,
    "start_date": "2026-08-19T06:00:00Z",
    "elapsed_time": 1600,
    "description": "felt good",
}


# --- compose_description -------------------------------------------------


def test_description_is_appended_after_existing_text(strava):
    assert (
        strava.compose_description("felt good", "https://open.spotify.com/playlist/x")
        == "felt good\n\nhttps://open.spotify.com/playlist/x"
    )


@pytest.mark.parametrize("empty", [None, "", "   ", "\n\n"])
def test_missing_description_yields_the_url_alone(strava, empty):
    """A null description used to render the literal string 'None'."""
    assert (
        strava.compose_description(empty, "https://open.spotify.com/playlist/x")
        == "https://open.spotify.com/playlist/x"
    )


def test_trailing_whitespace_does_not_add_extra_blank_lines(strava):
    assert (
        strava.compose_description("felt good\n\n", "https://x")
        == "felt good\n\nhttps://x"
    )


# --- get_latest_run ------------------------------------------------------


def call_get_latest_run(strava, responses):
    with mock.patch.object(
        strava, "get_strava_access_token_from_db", lambda user_id, db: "token"
    ), mock.patch.object(strava, "get", side_effect=responses):
        return strava.get_latest_run(user_id=1, db=None)


def test_returns_the_latest_activity(strava):
    result = call_get_latest_run(
        strava, [response(200, [{"id": 42}]), response(200, ACTIVITY)]
    )
    assert result["id"] == 42
    assert result["name"] == "The violin"
    assert result["url"] == "https://www.strava.com/activities/42"


def test_no_activities_raises_404_not_index_error(strava):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        call_get_latest_run(strava, [response(200, [])])
    assert excinfo.value.status_code == 404
    assert "any Strava activities" in excinfo.value.detail


@pytest.mark.parametrize("status", [401, 429, 500])
def test_non_200_when_listing_surfaces_the_status(strava, status):
    """Previously indexed straight into an error object and raised KeyError: 0."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        call_get_latest_run(strava, [response(status, {"message": "nope"})])
    assert excinfo.value.status_code == 502
    assert str(status) in excinfo.value.detail


def test_non_200_when_fetching_detail_surfaces_the_status(strava):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        call_get_latest_run(
            strava, [response(200, [{"id": 42}]), response(404, {"message": "gone"})]
        )
    assert excinfo.value.status_code == 502
    assert "404" in excinfo.value.detail
