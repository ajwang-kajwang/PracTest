"""Shared fixtures for the Py Kwon Do tests.

Plain functions rather than a test framework's fixtures, so the tests
run under tests/run_tests.py with nothing installed but NumPy and
matplotlib.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import competition as cp          # noqa: E402
import events as ev               # noqa: E402
import pykwondo as pk             # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_venue(clubs=("Alpha", "Beta"), mats=("Mat A", "Mat B")):
    """returns a venue with the given club areas and mats"""
    return pk.Venue.build_default(list(clubs), list(mats))


def make_competitors(venue, ranks, spec):
    """builds competitors from (name, age, club, rank) tuples"""
    people = []
    homes = {}
    for number, (name, age, club, rank) in enumerate(spec, start=1):
        area = venue.area(club)
        places = homes.setdefault(club, pk.standing_places(area, len(spec)))
        person = pk.Competitor(number, name, age, club, rank,
                               places[len(homes[club]) % len(places)],
                               skills=["pattern", "sparring", "team_pattern",
                                       "breaking"])
        person.home = person.get_pos()
        people.append(person)
    return people


def small_competition(events_list=None, seed=1, clubs=("Alpha", "Beta")):
    """returns a two-club competition ready to step"""
    ranks = pk.RankSystem()
    venue = make_venue(clubs=clubs)
    names = ["Ana", "Ben", "Cai", "Dev", "Eli", "Fay", "Gus", "Hal"]
    belts = ["White", "Yellow", "Green", "Blue", "Red", "Black",
             "Green", "Blue"]
    spec = [(names[i], 12 + i * 4, list(clubs)[i % len(clubs)], belts[i])
            for i in range(len(names))]
    people = []
    club_objects = {name: pk.Club(name) for name in clubs}
    for number, (name, age, club, rank) in enumerate(spec, start=1):
        area = venue.area(club)
        places = pk.standing_places(area, len(spec))
        person = pk.Competitor(number, name, age, club, rank,
                               places[number - 1],
                               skills=["pattern", "sparring", "team_pattern",
                                       "breaking"])
        person.home = person.get_pos()
        club_objects[club].add(person)
        people.append(person)
    schedule = events_list if events_list is not None else [
        ev.PatternEvent("Patterns", "Mat A"),
        ev.SparringEvent("Sparring", "Mat B", min_rank="Green"),
    ]
    return cp.Competition("Test Cup", venue, ranks, club_objects, people,
                          schedule, rng=random.Random(seed), max_parallel=2)


def walk_until(competition, condition, limit=200):
    """steps the competition until condition(competition) is true

    Returns
    -------
    bool
        True if the condition became true inside the step limit
    """
    steps = 0
    while steps < limit and not condition(competition):
        competition.step()
        steps += 1
    return condition(competition)
