"""Tests for the Competition scheduler and its results tracking."""
import helpers
import events as ev
import pykwondo as pk


def test_full_run_completes():
    """a whole competition runs to the end inside its budget"""
    competition = helpers.small_competition(seed=2)
    assert competition.run(400) is True
    assert all(event.is_finished() for event in competition.events)
    assert competition.step_no < 400


def test_full_run_returns_home():
    """everyone is back in their club area when it is over"""
    competition = helpers.small_competition(seed=3)
    competition.run(400)
    for person in competition.competitors:
        assert person.get_state() == pk.STATE_WAITING
        assert person.get_pos() == person.home
        assert person.is_free()


def test_eligible_are_called_up():
    """everyone eligible and free is entered automatically"""
    event = ev.PatternEvent("Patterns", "Mat A", min_rank="Green")
    competition = helpers.small_competition(events_list=[event])
    expected = {c.comp_id for c in event.eligible_pool(competition.competitors,
                                                       competition.ranks)}
    competition.step()
    assert {c.comp_id for c in event.entrants} == expected
    assert expected, "the fixture should have some eligible competitors"


def test_parallel_events_on_free_mats():
    """events with separate rank bands share the venue at the same time"""
    juniors = ev.PatternEvent("Juniors", "Mat A", max_rank="Yellow")
    seniors = ev.SparringEvent("Seniors", "Mat B", min_rank="Blue")
    competition = helpers.small_competition(events_list=[juniors, seniors])
    competition.step()
    assert len(competition.live_events()) == 2
    mats = {e.mat_name for e in competition.live_events()}
    assert mats == {"Mat A", "Mat B"}


def test_overlapping_eligibility_no_deadlock():
    """two events wanting the same people run one after the other

    This is the collision that silently empties both events if a
    competitor can be pulled off one mat by the other event starting.
    """
    first = ev.PatternEvent("Patterns One", "Mat A")
    second = ev.PatternEvent("Patterns Two", "Mat B")
    competition = helpers.small_competition(events_list=[first, second])
    competition.step()
    assert len(competition.live_events()) == 1, \
        "pools overlap - only one may run"
    assert competition.run(600) is True
    for event in (first, second):
        assert event.placings, f"{event.name} never produced results"
        assert len(event.entrants) == len(competition.competitors)


def test_points_awarded():
    """medal points reach both the individual and the club tables"""
    competition = helpers.small_competition(seed=4)
    competition.run(400)
    individuals = competition.standings()
    assert individuals[0].points > 0
    assert individuals[0].points >= individuals[-1].points
    club_points = {club.name: points for club, points, _ in
                   competition.club_standings()}
    assert sum(club_points.values()) == sum(c.points for c in
                                            competition.competitors)
    golds = {golds for _, _, golds in competition.club_standings()}
    assert max(golds) >= 1


def test_history_recorded():
    """every timestep is recorded for the after-the-fact plots"""
    competition = helpers.small_competition(seed=6)
    competition.run(400)
    table = competition.history_array()
    assert table.shape == (competition.step_no, 6)
    assert table[:, 0].tolist() == list(range(1, competition.step_no + 1))
    names, points = competition.club_points_array()
    assert points.shape == (competition.step_no, len(names))
    # club points never go down over the course of the day
    assert (points[1:] - points[:-1] >= 0).all()


def test_impossible_event_is_abandoned():
    """an event nobody can enter is dropped instead of blocking"""
    impossible = ev.SparringEvent("Grandmasters", "Mat A", min_age=90)
    normal = ev.PatternEvent("Patterns", "Mat B")
    competition = helpers.small_competition(events_list=[impossible, normal])
    assert competition.run(400) is True
    assert impossible.is_finished() and impossible.held is False
    assert normal.placings
