"""Tests for scenario loading, validation, rosters and the CLI."""
import glob
import os
import random

import helpers
import compSim
import pykwondo as pk
import scenario as sc

SCENARIOS = sorted(glob.glob(os.path.join(helpers.PROJECT, "scenarios",
                                          "*.json")))


def test_ask_int_revalidates():
    """out-of-range and non-numeric answers are re-prompted, not fatal"""
    answers = iter(["abc", "99", "", "3"])
    complaints = []
    value = sc.ask_int("How many", 1, 5, reader=lambda _: next(answers),
                       writer=complaints.append)
    assert value == 3
    assert len(complaints) == 3, complaints


def test_generated_roster_varies():
    """a generated roster has a mix of ranks, ages, clubs and skills"""
    ranks = pk.RankSystem()
    roster = sc.build_generated_roster(
        {"count": 30, "age_range": [10, 50]},
        ["Alpha", "Beta", "Gamma"], ranks, random.Random(1))
    assert len(roster) == 30
    assert len({entry["name"] for entry in roster}) == 30
    assert len({entry["rank"] for entry in roster}) > 2
    assert len({entry["club"] for entry in roster}) == 3
    assert len({entry["age"] for entry in roster}) > 5
    assert all(10 <= entry["age"] <= 50 for entry in roster)
    assert len({tuple(sorted(entry["skills"])) for entry in roster}) > 1


def test_venue_scales_with_clubs():
    """more clubs means more areas, still without overlaps"""
    small = pk.Venue.build_default(["A", "B"], ["Mat A"])
    large = pk.Venue.build_default(["A", "B", "C", "D", "E"],
                                   ["Mat A", "Mat B", "Mat C"])
    assert len(small.areas) == 2 + 2          # 2 clubs + mat + its queue
    assert len(large.areas) == 5 + 6
    areas = list(large.areas.values())
    for number, area in enumerate(areas):
        for other in areas[number + 1:]:
            assert not area.overlaps(other), \
                f"{area.name} overlaps {other.name}"


def test_custom_ranks():
    """a scenario can add belts without touching any code"""
    config = sc.default_config(competitors=12, clubs=2, event_count=2)
    config["ranks"] = [
        {"name": "White", "colour": "white", "skill": 30},
        {"name": "Brown", "colour": "saddlebrown", "skill": 60},
        {"name": "Black", "colour": "black", "skill": 85},
    ]
    config["events"][0].pop("max_rank", None)
    config["events"][1]["min_rank"] = "Brown"
    competition, _ = sc.Scenario(config).build(seed=1)
    assert competition.ranks.names() == ["White", "Brown", "Black"]
    assert competition.ranks.colour("Brown") == "saddlebrown"
    assert all(c.get_rank() in ("White", "Brown", "Black")
               for c in competition.competitors)


def test_load_each_scenario():
    """every shipped scenario file loads, validates and builds"""
    assert len(SCENARIOS) >= 3, "the report needs three showcase scenarios"
    for path in SCENARIOS:
        scenario = sc.Scenario.load(path)
        competition, steps = scenario.build()
        assert competition.competitors and competition.events
        assert steps > 0
        assert len(competition.events) >= 2
        mats = {area.name for area in competition.venue.areas_of_kind("mat")}
        for event in competition.events:
            assert event.mat_name in mats


def test_roster_csv():
    """the CSV roster is read with the right types and skills"""
    path = os.path.join(helpers.PROJECT, "scenarios",
                        "national_grading_roster.csv")
    roster = sc.load_roster(path)
    assert len(roster) > 20
    first = roster[0]
    assert isinstance(first["age"], int) and isinstance(first["form"], float)
    assert first["skills"] and isinstance(first["skills"], list)
    assert len({entry["club"] for entry in roster}) > 1


def test_seed_reproducible():
    """the same seed gives exactly the same competition twice"""
    path = os.path.join(helpers.PROJECT, "scenarios", "regional_titles.json")
    results = []
    for _ in range(2):
        competition, steps = sc.Scenario.load(path).build(seed=99)
        competition.run(steps)
        results.append((competition.step_no,
                        [(club.name, points) for club, points, _ in
                         competition.club_standings()],
                        [event.winner() for event in competition.events]))
    assert results[0] == results[1]


def test_bad_config_message():
    """a broken scenario explains what is wrong"""
    checks = [
        ({"name": "x", "clubs": ["A"]}, "events"),
        ({"name": "x", "clubs": [], "events": [{}, {}]}, "clubs"),
        ({"name": "x", "clubs": ["A"],
          "events": [{"type": "nope", "name": "n", "mat": "m"},
                     {"type": "pattern", "name": "p", "mat": "m"}]}, "nope"),
        ({"name": "x", "clubs": ["A"],
          "events": [{"type": "pattern", "name": "p", "mat": "m",
                      "min_rank": "Tartan"},
                     {"type": "pattern", "name": "q", "mat": "m"}]}, "Tartan"),
    ]
    for config, expected in checks:
        try:
            sc.validate_config(config)
            raise AssertionError(f"{config} should have been rejected")
        except ValueError as problem:
            assert expected in str(problem), \
                f"{expected} missing from {problem}"


def test_cli_parses():
    """the command line switches the showcase relies on all exist"""
    args = compSim.build_parser().parse_args(
        ["--scenario", "scenarios/regional_titles.json", "--seed", "5",
         "--steps", "250", "--no-animation", "--quiet"])
    assert args.scenario.endswith("regional_titles.json")
    assert (args.seed, args.steps) == (5, 250)
    assert args.no_animation and args.quiet
    plain = compSim.build_parser().parse_args([])
    assert plain.scenario is None and plain.no_animation is False


def test_prompted_scenario_builds():
    """answering the prompts produces a runnable scenario"""
    answers = iter(["2", "8", "2", "150"])
    scenario = sc.Scenario.from_prompt(reader=lambda _: next(answers),
                                       writer=lambda *_: None)
    competition, steps = scenario.build(seed=1)
    assert len(competition.competitors) == 8
    assert len(competition.clubs) == 2 and len(competition.events) == 2
    assert steps == 150
