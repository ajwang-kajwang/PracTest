"""Tests for the statistics, the saved report and the summary plots."""
import os
import tempfile

import helpers
import pykwondo as pk
import reporting


def finished_competition(seed=8):
    """returns a competition that has already been run"""
    competition = helpers.small_competition(seed=seed)
    competition.run(400)
    return competition


def test_counts():
    """the entry statistics add up to the field that turned up"""
    competition = finished_competition()
    by_rank = reporting.count_by_rank(competition.competitors,
                                      competition.ranks)
    by_club = reporting.count_by_club(competition.competitors)
    by_skill = reporting.count_by_skill(competition.competitors)
    assert sum(by_rank.values()) == len(competition.competitors)
    assert sum(by_club.values()) == len(competition.competitors)
    assert list(by_rank) == competition.ranks.names()
    assert set(by_club) == set(competition.clubs)
    assert by_skill["pattern"] == len(competition.competitors)


def test_report_contains_events():
    """the report names every event, its winner and both standings"""
    competition = finished_competition()
    text = reporting.report_text(competition, "Test Cup", "unit test", 8, 400,
                                 True)
    for event in competition.events:
        assert event.name in text
        assert event.winner() in text
    assert "Final standings - individuals" in text
    assert "Final standings - clubs" in text
    assert "Competitors at each rank" in text


def test_report_written():
    """the report, the results CSV and the plots all reach disk"""
    competition = finished_competition()
    with tempfile.TemporaryDirectory() as folder:
        report = reporting.write_report(competition,
                                        os.path.join(folder, "deep", "r.txt"),
                                        "Test Cup", "unit test", 8, 400, True)
        csv_path = reporting.write_results_csv(competition,
                                               os.path.join(folder, "r.csv"))
        plot = reporting.save_summary_plots(competition,
                                            os.path.join(folder, "r.png"))
        assert os.path.getsize(report) > 500
        assert os.path.getsize(plot) > 1000
        with open(csv_path, encoding="utf-8") as handle:
            rows = handle.read().splitlines()
        placings = sum(len(c.placings) for c in competition.competitors)
        assert len(rows) == placings + 1        # + header
        assert rows[0].startswith("competitor_id,")


def test_place_suffix():
    """placings read as 1st, 2nd, 3rd, 4th, 11th"""
    assert [reporting.place_suffix(n) for n in (1, 2, 3, 4, 11, 21)] == \
        ["st", "nd", "rd", "th", "th", "st"]


def test_live_view_uses_one_window():
    """the animation redraws one figure instead of opening more

    This is the PracTest3 Task 3 problem: plt.subplots() inside the
    loop opens a window per timestep.
    """
    import matplotlib.pyplot as plt

    import visualise

    plt.close("all")
    competition = helpers.small_competition(seed=9)
    view = visualise.SimView(competition, interactive=False)
    for _ in range(12):
        competition.step()
        view.update(competition)
    assert len(plt.get_fignums()) == 1, plt.get_fignums()
    with tempfile.TemporaryDirectory() as folder:
        frame = view.save(os.path.join(folder, "frame.png"))
        assert os.path.getsize(frame) > 1000
    view.close()


def test_status_text_lists_every_event():
    """the on-the-mats panel mentions each event"""
    import visualise

    competition = finished_competition()
    text = visualise.status_text(competition)
    for event in competition.events:
        assert visualise.shorten(event.name, 20) in text


def test_state_markers_cover_every_state():
    """every competitor state has a marker, so nobody is invisible"""
    import visualise

    states = {pk.STATE_WAITING, pk.STATE_TRAVELLING, pk.STATE_QUEUED,
              pk.STATE_STAGING, pk.STATE_COMPETING, pk.STATE_RETURNING}
    assert set(visualise.STATE_MARKERS) == states
