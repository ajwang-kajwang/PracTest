"""Tests for the world model: competitors, ranks and the venue."""
import random

import helpers
import characters
import pykwondo as pk


def test_competitor_extends_student():
    """Competitor is a Student, so the given helpers still work on it"""
    person = pk.Competitor(1, "Ana", 20, "Alpha", "Green", (3, 3))
    assert isinstance(person, characters.Student)
    names = characters.get_namelist([person])
    colours, numbers = characters.get_ranklist([person],
                                               pk.RankSystem().names())
    assert names == ["Ana"] and colours == ["Green"] and numbers == [2]


def test_competitor_attributes():
    """every attribute the specification lists is present"""
    person = pk.Competitor(7, "Ben", 31, "Beta", "Blue", (4, 5),
                           skills=["pattern", "sparring"])
    assert (person.get_id(), person.get_name(), person.get_age()) == \
        (7, "Ben", 31)
    assert person.get_club() == "Beta" and person.get_rank() == "Blue"
    assert person.get_pos() == (4, 5) and person.get_direction() == (0, -1)
    assert person.has_skill("sparring") and not person.has_skill("breaking")


def test_competitor_str():
    """__str__ shows the useful state, not just the name"""
    text = str(pk.Competitor(2, "Cai", 15, "Alpha", "White", (1, 2)))
    assert "Cai" in text and "White" in text and "(1, 2)" in text
    assert "waiting" in text and "Alpha" in text


def test_step_change_targets():
    """with a target the competitor takes one Moore step towards it"""
    venue = helpers.make_venue()
    person = pk.Competitor(1, "Ana", 20, "Alpha", "Green", (5, 5))
    person.set_target((8, 5))
    assert person.step_change(venue=venue) is True
    assert person.get_pos() == (6, 5)
    person.set_target((7, 4))
    person.step_change(venue=venue)
    assert person.get_pos() == (7, 4) and person.at_target()
    # standing on the target means standing still
    assert person.step_change(venue=venue) is False


def test_step_change_set_move():
    """set_move is honoured - the bug in the given code, fixed in PT3"""
    student = characters.Student("Shifu", (2, 2), "Black")
    student.step_change(set_move=(1, 0))
    assert student.get_pos() == (3, 2), "given Student must apply set_move"

    venue = helpers.make_venue()
    person = pk.Competitor(1, "Ana", 20, "Alpha", "Green", (5, 5))
    person.step_change(set_move=(-1, 1), venue=venue)
    assert person.get_pos() == (4, 6)


def test_state_transitions():
    """a competitor walks out, competes and comes home again"""
    competition = helpers.small_competition()
    person = competition.competitors[0]
    assert person.get_state() == pk.STATE_WAITING and person.is_free()
    reached = helpers.walk_until(
        competition, lambda c: person.get_state() == pk.STATE_COMPETING)
    assert reached, "nobody ever reached the mat"
    assert not person.is_free()
    home_again = helpers.walk_until(
        competition, lambda c: person.get_state() == pk.STATE_WAITING,
        limit=300)
    assert home_again and person.get_pos() == person.home
    assert person.is_free()


def test_direction_updates():
    """moving turns the competitor to face the way it moved"""
    venue = helpers.make_venue()
    person = pk.Competitor(1, "Ana", 20, "Alpha", "Green", (5, 5))
    person.set_target((5, 9))
    person.step_change(venue=venue)
    assert person.get_direction() == (0, 1) and person.facing() == "S"
    person.set_target((9, 9))          # down and to the right: a diagonal
    person.step_change(venue=venue)
    assert person.facing() == "SE"
    person.set_target((12, person.get_pos()[1]))
    person.step_change(venue=venue)
    assert person.facing() == "E"


def test_rank_order():
    """ranks are ordered, so eligibility is an index comparison"""
    ranks = pk.RankSystem()
    assert ranks.index("White") == 0
    assert ranks.index("Black") == len(ranks) - 1
    assert ranks.is_between("Green", "Yellow", "Blue")
    assert not ranks.is_between("White", "Blue", None)
    assert ranks.band("Blue", None)[0] == "Blue"


def test_rank_affects_performance():
    """a higher belt scores better on average than a lower one"""
    ranks = pk.RankSystem()
    rng = random.Random(3)
    white = pk.Competitor(1, "Low", 24, "Alpha", "White", (2, 2))
    black = pk.Competitor(2, "High", 24, "Alpha", "Black", (2, 3))
    white_mean = sum(white.performance(ranks, rng) for _ in range(200)) / 200
    black_mean = sum(black.performance(ranks, rng) for _ in range(200)) / 200
    assert black_mean > white_mean + 20


def test_venue_grid_codes():
    """the grid is walls, floor and one code per area"""
    venue = helpers.make_venue()
    grid = venue.grid()
    assert len(grid) == venue.height and len(grid[0]) == venue.width
    assert grid[0][0] == pk.CODE_WALL and grid[-1][-1] == pk.CODE_WALL
    mat = venue.area("Mat A")
    assert grid[mat.y0][mat.x0] == mat.code
    assert len(venue.colour_table()) == 2 + len(venue.areas)
    assert venue.area_at(mat.centre()).name == "Mat A"


def test_barrier_blocks_move():
    """nobody walks through the wall, even aiming straight at it"""
    venue = helpers.make_venue()
    person = pk.Competitor(1, "Ana", 20, "Alpha", "Green", (1, 1))
    person.set_target((-5, -5))
    for _ in range(10):
        person.step_change(venue=venue)
    assert venue.is_walkable(person.get_pos())
    assert person.get_pos() == (1, 1)
