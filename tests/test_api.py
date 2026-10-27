import sys

import pytest

api = sys.modules["shl_scoreboard_standalone.api"]


def event(**overrides):
    base = {
        "idEvent": "2476577",
        "idLeague": "4419",
        "strTimestamp": "2026-10-27T18:00:00",
        "dateEvent": "2026-10-27",
        "strTime": "18:00:00",
        "strHomeTeam": "Frölunda HC",
        "strAwayTeam": "Rögle BK",
        "strHomeTeamBadge": "https://example.com/fhc.png",
        "strAwayTeamBadge": "https://example.com/rbk.png",
        "intHomeScore": None,
        "intAwayScore": None,
        "intRound": "27",
        "strStatus": "NS",
        "strVenue": "Scandinavium",
        "strSeason": "2026-2027",
    }
    base.update(overrides)
    return base


def test_pre_game():
    game = api.parse_event(event())
    assert game["game_state"] == 0
    assert game["status"] == ""
    assert game["start_time"] == "2026-10-27T18:00:00+00:00"
    assert (game["home_abbr"], game["away_abbr"]) == ("FHC", "RBK")
    assert game["home_score"] is None
    assert game["round"] == 27


@pytest.mark.parametrize(
    ("status", "state", "text"),
    [("2P", 1, "2nd"), ("FT", 2, "Final"), ("AOT", 2, "Final/OT"), ("AP", 2, "Final/SO"), ("PST", 0, "Postponed")],
)
def test_statuses(status, state, text):
    game = api.parse_event(event(strStatus=status, intHomeScore="3", intAwayScore="2"))
    assert game["game_state"] == state
    assert game["status"] == text
    if state:
        assert (game["home_score"], game["away_score"]) == (3, 2)


def test_unknown_abbreviation_falls_back():
    assert api.team_abbr("Nya Laget IF") == "NYA"


def test_team_filter_by_abbr_and_name():
    games = [api.parse_event(event()), api.parse_event(event(idEvent="2", strHomeTeam="Luleå HF", strAwayTeam="HV71"))]
    assert [g["id"] for g in api.build_games([event()], ["fhc"])] == ["2476577"]
    assert len(api.build_games([event(), event(idEvent="2", strHomeTeam="Luleå HF", strAwayTeam="HV71")], ["luleå"])) == 1
    assert len(api.build_games([event()], ["HV71"])) == 0
    assert len(games) == 2


def test_build_games_dedupes_and_sorts():
    late = event(idEvent="b", strTimestamp="2026-10-27T19:00:00")
    early = event(idEvent="a", strTimestamp="2026-10-27T16:00:00")
    games = api.build_games([late, early, late], None)
    assert [g["id"] for g in games] == ["a", "b"]
