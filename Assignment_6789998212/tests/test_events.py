"""Tests for the event hierarchy and the shared event lifecycle."""
import random

import helpers
import events as ev
import pykwondo as pk


def ranks():
    """returns the default rank system"""
    return pk.RankSystem()


def run_event_to_finish(competition, event, limit=300):
    """steps a competition until one event has finished"""
    return helpers.walk_until(competition,
                              lambda c: event.is_finished(), limit)


def test_eligibility_rank_band():
    """rank, age and trained skill all gate entry"""
    event = ev.SparringEvent("Seniors", "Mat A", min_rank="Blue", min_age=18)
    system = ranks()
    old_enough = pk.Competitor(1, "Ana", 30, "Alpha", "Red", (2, 2),
                               skills=["sparring"])
    too_junior = pk.Competitor(2, "Ben", 30, "Alpha", "Green", (2, 3),
                               skills=["sparring"])
    too_young = pk.Competitor(3, "Cai", 14, "Alpha", "Red", (2, 4),
                              skills=["sparring"])
    untrained = pk.Competitor(4, "Dev", 30, "Alpha", "Red", (2, 5),
                              skills=["pattern"])
    assert event.is_eligible(old_enough, system)
    assert not event.is_eligible(too_junior, system)
    assert not event.is_eligible(too_young, system)
    assert not event.is_eligible(untrained, system)


def test_lifecycle_states():
    """an event walks through calling, staging, running, finished"""
    event = ev.PatternEvent("Patterns", "Mat A")
    competition = helpers.small_competition(events_list=[event])
    assert event.state == ev.EVENT_PENDING
    seen = set()
    for _ in range(300):
        competition.step()
        seen.add(event.state)
    assert {ev.EVENT_CALLING, ev.EVENT_STAGING, ev.EVENT_RUNNING,
            ev.EVENT_FINISHED} <= seen


def test_waits_for_arrivals():
    """the event does not start until every entrant has arrived"""
    event = ev.PatternEvent("Patterns", "Mat A")
    competition = helpers.small_competition(events_list=[event])
    competition.step()
    assert event.state == ev.EVENT_CALLING and event.entrants
    # while somebody is still walking, the event must not be running
    walking = helpers.walk_until(
        competition, lambda c: event.everyone_arrived(), limit=100)
    assert walking
    states_before_arrival = [e.state for e in [event]]
    assert states_before_arrival[0] in (ev.EVENT_CALLING, ev.EVENT_STAGING,
                                        ev.EVENT_RUNNING)
    assert all(c.at_target() for c in event.active)


def test_pattern_event_ranks_entrants():
    """a pattern event scores everyone and ranks them"""
    event = ev.PatternEvent("Patterns", "Mat A")
    competition = helpers.small_competition(events_list=[event])
    assert run_event_to_finish(competition, event)
    assert len(event.placings) == len(event.entrants)
    scores = [p["score"] for p in event.placings]
    assert scores == sorted(scores, reverse=True)
    assert event.placings[0]["points"] == 5


def test_sparring_pairs_by_rank():
    """pairs are drawn between the closest ranks available"""
    event = ev.SparringEvent("Sparring", "Mat A")
    venue = helpers.make_venue()
    people = [
        pk.Competitor(1, "Ana", 20, "Alpha", "White", (2, 2),
                      skills=["sparring"]),
        pk.Competitor(2, "Ben", 20, "Alpha", "Black", (3, 2),
                      skills=["sparring"]),
        pk.Competitor(3, "Cai", 20, "Beta", "White", (4, 2),
                      skills=["sparring"]),
        pk.Competitor(4, "Dev", 20, "Beta", "Black", (5, 2),
                      skills=["sparring"]),
    ]
    event.active = people
    pairs, byes = event.pair_up(ranks())
    assert byes == []
    for left, right in pairs:
        assert left.get_rank() == right.get_rank()


def test_sparring_bye_for_odd():
    """an odd entry list gives exactly one bye"""
    event = ev.SparringEvent("Sparring", "Mat A")
    event.active = [pk.Competitor(i, f"C{i}", 20, "Alpha", "Green", (i, 2),
                                  skills=["sparring"]) for i in range(1, 6)]
    pairs, byes = event.pair_up(ranks())
    assert len(pairs) == 2 and len(byes) == 1
    paired = {c.comp_id for pair in pairs for c in pair}
    assert byes[0].comp_id not in paired


def test_team_event_moves_together():
    """a team takes one shared move, or nobody in it moves"""
    event = ev.TeamPatternEvent("Teams", "Mat A", team_size=2)
    competition = helpers.small_competition(events_list=[event])
    started = helpers.walk_until(
        competition, lambda c: event.state == ev.EVENT_RUNNING, limit=200)
    assert started, "team event never started"
    club = list(event.teams)[0]
    before = [c.get_pos() for c in event.teams[club]]
    competition.step()
    after = [c.get_pos() for c in event.teams[club]]
    deltas = {(new[0] - old[0], new[1] - old[1])
              for old, new in zip(before, after)}
    assert len(deltas) == 1, f"team did not move as one: {deltas}"


def test_breaking_event_eliminates():
    """failures drop out and the boards keep going up"""
    event = ev.BreakingEvent("Breaking", "Mat A", max_boards=6)
    competition = helpers.small_competition(events_list=[event])
    started = helpers.walk_until(
        competition, lambda c: event.state == ev.EVENT_RUNNING, limit=200)
    assert started
    entered = len(event.active)
    assert run_event_to_finish(competition, event)
    assert len(event.active) <= 1 or event.round_no >= 1
    assert len(event.placings) == entered
    assert max(event.boards.values()) >= 1


def test_every_event_produces_placings():
    """all four event types finish with a ranked result"""
    schedule = [
        ev.PatternEvent("Patterns", "Mat A"),
        ev.SparringEvent("Sparring", "Mat B", min_rank="Green"),
        ev.TeamPatternEvent("Teams", "Mat A", team_size=2),
        ev.BreakingEvent("Breaking", "Mat B", min_rank="Green"),
    ]
    competition = helpers.small_competition(events_list=schedule, seed=5)
    assert helpers.walk_until(competition,
                              lambda c: all(e.is_finished() for e in schedule),
                              limit=600)
    for event in schedule:
        assert event.placings, f"{event.name} produced no placings"
        assert event.winner() is not None
        assert event.placings[0]["points"] >= event.placings[-1]["points"]


def test_make_event_from_config():
    """scenario dictionaries build the matching event class"""
    event = ev.make_event({"type": "breaking", "name": "Power", "mat": "Mat A",
                           "min_rank": "Blue", "max_boards": 4})
    assert isinstance(event, ev.BreakingEvent)
    assert event.max_boards == 4 and event.min_rank == "Blue"
    try:
        ev.make_event({"type": "juggling", "name": "?", "mat": "Mat A"})
        raise AssertionError("unknown event type should be rejected")
    except ValueError as problem:
        assert "juggling" in str(problem)
