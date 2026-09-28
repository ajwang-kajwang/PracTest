#
# pykwondo.py - core model for the Py Kwon Do martial arts simulation
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# This module holds the "world": the rank system, the clubs, the
# competitors and the venue they move around in.  The events live in
# events.py and the thing that runs them all lives in competition.py.
#
# Sources / self-citation
# -----------------------
# * Student, get_namelist(), get_ranklist() - unit given code, imported
#   from characters.py (see that file's header).
# * Competitor.step_change() keeps the set_move= contract of the given
#   Student.step_change(), fixed in my Practical Test 3 Task 4.
# * Venue.grid() is the PracTest3 Task 2 floor array (an integer code
#   per cell, drawn with imshow/vmin/vmax) widened so that every area
#   has its own code and colour.
# * Venue.is_walkable() is the PracTest3 Task 4 "check the move before
#   committing to it" barrier test, moved onto the venue so that both
#   individual and group moves can share it.
#
import math
import random

from characters import Student

# --- competitor states -------------------------------------------------
# A competitor is always in exactly one of these.  Nearly all of the
# simulation logic is "what do I do while I am in this state", which is
# why the state lives on the competitor rather than in the main loop.
STATE_WAITING = "waiting"        # in the club area, nothing to do
STATE_TRAVELLING = "travelling"  # walking to an event queue
STATE_QUEUED = "queued"          # standing in the queue, event not started
STATE_STAGING = "staging"        # walking from the queue onto the mat
STATE_COMPETING = "competing"    # on the mat, event running
STATE_RETURNING = "returning"    # walking back to the club area

# --- venue cell codes --------------------------------------------------
# Codes 0 and 1 are fixed; area codes are handed out from FIRST_AREA_CODE
# upwards as areas are added, exactly like PracTest3's floor used 10 for
# the border and 5 for the centre, just with more than two values.
CODE_WALL = 0
CODE_FLOOR = 1
FIRST_AREA_CODE = 2

WALL_COLOUR = "#2b2b2b"
FLOOR_COLOUR = "#d9d4c9"

# Default belt colours, extending the given
# rank_defs = ["White", "Yellow", "Green", "Blue", "Black"].
# "colour" is what matplotlib draws; "skill" is the base performance
# rating of that belt, which is how rank affects performance.
DEFAULT_RANKS = [
    {"name": "White", "colour": "white", "skill": 35},
    {"name": "Yellow", "colour": "gold", "skill": 45},
    {"name": "Green", "colour": "forestgreen", "skill": 56},
    {"name": "Blue", "colour": "royalblue", "skill": 66},
    {"name": "Red", "colour": "crimson", "skill": 76},
    {"name": "Black", "colour": "black", "skill": 86},
]

# The eight Moore-neighbourhood facings, named for printing.  y grows
# downwards because imshow() draws row 0 at the top (PracTest3 note).
COMPASS = {
    (0, -1): "N", (1, -1): "NE", (1, 0): "E", (1, 1): "SE",
    (0, 1): "S", (-1, 1): "SW", (-1, 0): "W", (-1, -1): "NW",
}


def sign(value):
    """returns -1, 0 or 1 - the one-cell step that reduces value"""
    return (value > 0) - (value < 0)


def step_towards(pos, target):
    """returns the Moore-neighbourhood (dx, dy) that moves pos to target

    One cell per timestep at most, diagonals allowed, which is the same
    neighbourhood the given Student.step_change() picks from at random.
    """
    return (sign(target[0] - pos[0]), sign(target[1] - pos[1]))


class RankSystem:
    """
    The ordered set of belts used by a simulation.

    Rank is stored as a plain string on the Competitor (as in the given
    code), and everything that needs to compare ranks - event
    eligibility, sparring pairings, performance - goes through this
    class.  Because the ranks are an ordered list, "is this belt high
    enough" is an index comparison, and adding a belt colour is one
    entry in the scenario file and no code change at all.

    Attributes
    ----------
    ranks : list
        list of dicts, lowest belt first, each with name/colour/skill
    """

    def __init__(self, ranks=None):
        """builds the rank system, defaulting to DEFAULT_RANKS"""
        source = DEFAULT_RANKS if ranks is None else ranks
        if len(source) < 2:
            raise ValueError("a rank system needs at least two ranks")
        self.ranks = [dict(rank) for rank in source]
        names = self.names()
        if len(set(names)) != len(names):
            raise ValueError(f"duplicate rank names: {names}")

    def __len__(self):
        """returns how many ranks exist"""
        return len(self.ranks)

    def __str__(self):
        """returns the belts lowest to highest"""
        return " < ".join(self.names())

    def names(self):
        """returns the rank names, lowest first"""
        return [rank["name"] for rank in self.ranks]

    def colours(self):
        """returns the plot colour of each rank, lowest first"""
        return [rank["colour"] for rank in self.ranks]

    def index(self, name):
        """returns the position of a rank in the order (0 = lowest)"""
        found = [i for i, rank in enumerate(self.ranks)
                 if rank["name"] == name]
        if not found:
            raise ValueError(f"unknown rank {name!r}, expected one of "
                             f"{self.names()}")
        return found[0]

    def colour(self, name):
        """returns the plot colour for a rank name"""
        return self.ranks[self.index(name)]["colour"]

    def skill(self, name):
        """returns the base skill rating for a rank name"""
        return self.ranks[self.index(name)]["skill"]

    def is_between(self, name, lowest=None, highest=None):
        """returns True if a rank sits inside an inclusive rank band"""
        position = self.index(name)
        low = 0 if lowest is None else self.index(lowest)
        high = len(self.ranks) - 1 if highest is None else self.index(highest)
        return low <= position <= high

    def band(self, lowest=None, highest=None):
        """returns the rank names inside an inclusive rank band"""
        return [name for name in self.names()
                if self.is_between(name, lowest, highest)]


class Club:
    """
    A club: a named group of competitors with its own area of the venue.

    Attributes
    ----------
    name : str
        the club's name
    area_name : str
        the name of the Venue area the club waits in
    members : list
        the club's Competitors
    points : int
        medal points won by the club's members
    """

    def __init__(self, name, area_name=None):
        """creates an empty club"""
        self.name = name
        self.area_name = area_name if area_name else name
        self.members = []
        self.points = 0

    def __str__(self):
        """returns the club name and size"""
        return f"{self.name} ({len(self.members)} competitors)"

    def add(self, competitor):
        """adds a competitor to the club"""
        self.members.append(competitor)

    def size(self):
        """returns the number of members"""
        return len(self.members)


class Competitor(Student):
    """
    A competitor at the competition - a Student that also knows which
    club it belongs to, what it is allowed to enter, which way it is
    facing and what it is currently doing.

    Subclassing Student (rather than wrapping one) keeps the given
    helpers get_namelist()/get_ranklist() working on competitors, and
    keeps the given step_change(set_move=...) contract that the group
    events rely on.

    Attributes
    ----------
    comp_id : int
        competitor number, unique within a competition
    name, pos, rank : see Student
    age : int
        age in years, used for age-restricted events and performance
    club : str
        name of the club the competitor represents
    skills : list
        names of the event types this competitor can enter
    direction : tuple
        (dx, dy) unit vector the competitor is facing
    state : str
        one of the STATE_* constants
    home : tuple
        the spot in the club area this competitor waits at
    target : tuple or None
        where the competitor is currently walking to
    current_event : Event or None
        the event that currently owns this competitor
    form : float
        per-competitor multiplier, so two Blue belts are not identical
    placings : list
        (event name, place, score) for every event entered
    points : int
        medal points won

    Methods
    -------
    step_change(set_move=None, venue=None)
        one timestep of movement - towards target, or a supplied move
    set_target(pos) / at_target() / clear_target()
        goal-directed movement support
    is_free() / assign_event(event) / release()
        the one-event-at-a-time lock
    performance(ranks, rng, difficulty)
        how well this competitor does one scored attempt
    """

    def __init__(self, comp_id, name, age, club, rank, pos,
                 skills=None, form=1.0, direction=(0, -1)):
        """initialises the competitor, starting in the waiting state"""
        super().__init__(name, pos, rank)
        self.comp_id = comp_id
        self.age = age
        self.club = club
        self.skills = list(skills) if skills else []
        self.form = form
        self.direction = direction
        self.state = STATE_WAITING
        self.home = pos
        self.target = None
        self.current_event = None
        self.placings = []
        self.points = 0

    def __str__(self):
        """returns the competitor's key information as one line

        Extends the PracTest3 Task 1.d version of Student.__str__() with
        the attributes the assignment adds (id, club, state, facing).
        """
        return (f"#{self.comp_id:<3} {self.name:<12} {self.rank:<6} "
                f"{self.club:<16} age {self.age:<3} {str(self.pos):<10} "
                f"facing {self.facing():<2} [{self.state}]")

    # --- simple accessors ---------------------------------------------
    def get_id(self):
        """returns the competitor's ID number"""
        return self.comp_id

    def get_club(self):
        """returns the name of the competitor's club"""
        return self.club

    def get_age(self):
        """returns the competitor's age"""
        return self.age

    def get_state(self):
        """returns the current state string"""
        return self.state

    def get_direction(self):
        """returns the (dx, dy) unit vector the competitor faces"""
        return self.direction

    def facing(self):
        """returns the compass name of the current facing, e.g. 'NE'"""
        return COMPASS.get(self.direction, "-")

    def has_skill(self, skill):
        """returns True if the competitor trains this kind of event"""
        return skill is None or skill in self.skills

    # --- goal-directed movement ---------------------------------------
    def set_target(self, pos):
        """gives the competitor a cell to walk to"""
        self.target = pos

    def clear_target(self):
        """forgets the current target"""
        self.target = None

    def at_target(self):
        """returns True when standing on the target (or having none)"""
        return self.target is None or self.pos == self.target

    def face(self, move):
        """updates the facing direction, ignoring a zero move"""
        if move != (0, 0):
            self.direction = move

    def face_towards(self, pos):
        """turns to face another cell without moving"""
        self.face(step_towards(self.pos, pos))

    def step_change(self, set_move=None, venue=None):
        """moves the competitor one cell for this timestep

        Replaces the given random walk with goal-directed movement:
        with no set_move the competitor takes the single Moore step
        that gets it closer to its target, and stands still once it has
        arrived or has no target.  A set_move is applied as given,
        which is what the group/synchronised events use - the same
        contract as the given Student.step_change(set_move=...) once
        PracTest3 Task 4.c had fixed it.

        If a venue is supplied the move is checked against it before
        being committed (the PracTest3 Task 4 barrier check).  A blocked
        diagonal falls back to sliding along one axis, so competitors
        walk around a wall corner instead of getting stuck on it.

        Parameters
        ----------
        set_move : tuple, optional
            (dx, dy) move supplied from outside
        venue : Venue, optional
            venue used to reject moves into a wall

        Returns
        -------
        bool
            True if the competitor actually moved this timestep
        """
        if set_move is not None:
            wanted = tuple(set_move)
        elif not self.at_target():
            wanted = step_towards(self.pos, self.target)
        else:
            wanted = (0, 0)

        if wanted == (0, 0):
            return False

        # Try the move we want, then each single-axis half of it, so a
        # blocked diagonal still makes progress along a wall.
        options = [wanted]
        if wanted[0] != 0 and wanted[1] != 0:
            options.extend([(wanted[0], 0), (0, wanted[1])])
        allowed = [move for move in options
                   if venue is None or venue.is_walkable(self._shift(move))]
        if not allowed:
            self.face(wanted)   # blocked, but still turn to face the way
            return False

        move = allowed[0]
        self.set_pos(self._shift(move))
        self.face(move)
        return True

    def _shift(self, move):
        """returns this competitor's position offset by a move"""
        return (self.pos[0] + move[0], self.pos[1] + move[1])

    # --- the one-event-at-a-time lock ---------------------------------
    def is_free(self):
        """returns True if no event currently owns this competitor"""
        return self.current_event is None

    def assign_event(self, event):
        """locks the competitor into an event"""
        self.current_event = event

    def release(self):
        """releases the competitor and sends it back to its club area"""
        self.current_event = None
        self.state = STATE_RETURNING
        self.set_target(self.home)

    def go_home(self):
        """puts a competitor back in its club area immediately"""
        self.set_pos(self.home)
        self.clear_target()
        self.current_event = None
        self.state = STATE_WAITING

    # --- performance ---------------------------------------------------
    def age_factor(self):
        """returns the age multiplier, peaking in the mid twenties"""
        return 1.0 - abs(self.age - 24) / 120.0

    def performance(self, ranks, rng, difficulty=1.0):
        """scores one attempt out of 100

        Rank sets the base skill, the competitor's own form and age
        adjust it, the event's difficulty scales it down and a random
        term stops any two attempts being identical.
        """
        base = ranks.skill(self.rank) * self.form * self.age_factor()
        score = base / difficulty + rng.gauss(0.0, 6.0)
        return round(min(100.0, max(0.0, score)), 1)

    def record_placing(self, event_name, place, score, points):
        """records a result for this competitor"""
        self.placings.append((event_name, place, score))
        self.points += points


class Area:
    """
    A named rectangle of the venue - a club's waiting area, an event
    mat, or the queue beside a mat.

    Bounds are inclusive, in (x, y) cell coordinates.

    Attributes
    ----------
    name : str
        the area's name, unique within a venue
    kind : str
        'club', 'mat' or 'queue'
    code : int
        the value written into the venue grid for this area
    colour : str
        the colour the area is drawn in
    x0, y0, x1, y1 : int
        inclusive bounds of the rectangle
    """

    def __init__(self, name, kind, code, colour, x0, y0, x1, y1):
        """creates an area, checking the rectangle is the right way round"""
        if x1 < x0 or y1 < y0:
            raise ValueError(f"area {name!r} has an empty rectangle")
        self.name = name
        self.kind = kind
        self.code = code
        self.colour = colour
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    def __str__(self):
        """returns the area name and bounds"""
        return (f"{self.name} [{self.kind}] "
                f"({self.x0},{self.y0})-({self.x1},{self.y1})")

    def width(self):
        """returns the area's width in cells"""
        return self.x1 - self.x0 + 1

    def height(self):
        """returns the area's height in cells"""
        return self.y1 - self.y0 + 1

    def capacity(self):
        """returns how many cells the area has"""
        return self.width() * self.height()

    def centre(self):
        """returns the (x, y) middle cell of the area"""
        return ((self.x0 + self.x1) // 2, (self.y0 + self.y1) // 2)

    def contains(self, pos):
        """returns True if a position is inside this area"""
        return self.x0 <= pos[0] <= self.x1 and self.y0 <= pos[1] <= self.y1

    def overlaps(self, other):
        """returns True if two areas share any cell"""
        return not (self.x1 < other.x0 or other.x1 < self.x0
                    or self.y1 < other.y0 or other.y1 < self.y0)

    def slots(self, count, spacing=2, from_row=None):
        """returns up to count evenly spread standing positions

        Positions are handed out row by row from the top of the area,
        every `spacing` cells, so competitors stand in tidy lines with
        room between them rather than on top of each other.

        Parameters
        ----------
        count : int
            how many positions are wanted
        spacing : int
            cells between neighbours (2 leaves a gap)
        from_row : int, optional
            first row to use, defaults to the top row of the area

        Returns
        -------
        list
            list of (x, y) positions, length min(count, what fits)
        """
        first_row = self.y0 if from_row is None else from_row
        rows = range(first_row, self.y1 + 1, spacing)
        cols = range(self.x0, self.x1 + 1, spacing)
        places = [(x, y) for y in rows for x in cols]
        return places[:count]

    def pair_slots(self, pairs, spacing=3):
        """returns (left, right) facing positions for paired competitors

        Used by sparring: each pair stands two cells apart on the same
        row, facing each other, with pairs stacked down the mat.
        """
        rows = list(range(self.y0 + 1, self.y1, spacing))
        middle = (self.x0 + self.x1) // 2
        return [((middle - 1, row), (middle + 1, row)) for row in rows[:pairs]]


class Venue:
    """
    The competition venue: a grid of coded cells plus the named areas
    that gave those cells their codes.

    The grid is the PracTest3 floor array grown up - one integer per
    cell, drawn with imshow() - and every area's coordinates live in one
    Area object, so events and movement ask the venue where a mat is
    instead of hard-coding coordinates.

    Attributes
    ----------
    width, height : int
        size of the floor in cells
    areas : dict
        name -> Area
    """

    def __init__(self, width, height):
        """creates a walled, empty venue"""
        if width < 10 or height < 10:
            raise ValueError("a venue needs to be at least 10x10 cells")
        self.width = width
        self.height = height
        self.areas = {}
        self._next_code = FIRST_AREA_CODE

    def __str__(self):
        """returns the venue size and area count"""
        return f"Venue {self.width}x{self.height}, {len(self.areas)} areas"

    def add_area(self, name, kind, colour, x0, y0, x1, y1):
        """adds a named area, rejecting overlaps and out-of-bounds boxes"""
        if name in self.areas:
            raise ValueError(f"venue already has an area called {name!r}")
        if not (1 <= x0 and x1 <= self.width - 2
                and 1 <= y0 and y1 <= self.height - 2):
            raise ValueError(f"area {name!r} does not fit inside the walls")
        area = Area(name, kind, self._next_code, colour, x0, y0, x1, y1)
        clashes = [other.name for other in self.areas.values()
                   if area.overlaps(other)]
        if clashes:
            raise ValueError(f"area {name!r} overlaps {clashes}")
        self.areas[name] = area
        self._next_code += 1
        return area

    def area(self, name):
        """returns an area by name"""
        if name not in self.areas:
            raise ValueError(f"unknown venue area {name!r}, "
                             f"have {sorted(self.areas)}")
        return self.areas[name]

    def areas_of_kind(self, kind):
        """returns the areas of one kind, in the order they were added"""
        return [area for area in self.areas.values() if area.kind == kind]

    def grid(self):
        """returns the floor as a 2D list of cell codes, indexed [y][x]

        Row 0 is the top of the picture, because imshow() draws it
        there - positions are (x, y) with y growing downwards, as in
        PracTest3.
        """
        floor = [[CODE_FLOOR] * self.width for _ in range(self.height)]
        edges = [(x, y) for y in range(self.height) for x in range(self.width)
                 if x in (0, self.width - 1) or y in (0, self.height - 1)]
        for x, y in edges:
            floor[y][x] = CODE_WALL
        for area in self.areas.values():
            for y in range(area.y0, area.y1 + 1):
                for x in range(area.x0, area.x1 + 1):
                    floor[y][x] = area.code
        return floor

    def colour_table(self):
        """returns the colour for every code, in code order

        Fed straight to a ListedColormap so each area draws in its own
        colour instead of the single Greys ramp PracTest3 used.
        """
        table = [WALL_COLOUR, FLOOR_COLOUR]
        table.extend(area.colour for area in
                     sorted(self.areas.values(), key=lambda a: a.code))
        return table

    def is_inside(self, pos):
        """returns True if a position is on the grid at all"""
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    def is_walkable(self, pos):
        """returns True if a competitor may stand on this cell

        The walls are the only barrier - mats and club areas are all
        walkable floor.  This is the PracTest3 Task 4 check, asked
        before a move is committed rather than after.
        """
        return (self.is_inside(pos)
                and 0 < pos[0] < self.width - 1
                and 0 < pos[1] < self.height - 1)

    def area_at(self, pos):
        """returns the Area covering a position, or None for bare floor"""
        covering = [area for area in self.areas.values() if area.contains(pos)]
        return covering[0] if covering else None

    @classmethod
    def build_default(cls, club_names, mat_names, width=None, height=None,
                      club_colour="#bcd4e6", mat_colours=None,
                      queue_colour="#efe0b9"):
        """lays out a venue from the clubs and mats a scenario asks for

        Club areas go in a strip along the bottom of the floor, one per
        club.  Mats are packed into a grid above them, each with a queue
        strip along its bottom edge.  Sizes are derived from the counts,
        so changing the number of clubs or events in a scenario file
        changes the venue with no code change (feature 7).

        Parameters
        ----------
        club_names : list
            names of the clubs, one area each
        mat_names : list
            names of the event mats, one area (plus queue) each
        width, height : int, optional
            floor size; worked out from the counts when not given
        club_colour, queue_colour : str
            colours for those areas
        mat_colours : list, optional
            colour per mat, cycled if shorter than mat_names

        Returns
        -------
        Venue
        """
        if not club_names:
            raise ValueError("a venue needs at least one club")
        if not mat_names:
            raise ValueError("a venue needs at least one mat")
        palette = mat_colours if mat_colours else [
            "#f6c9c9", "#c9f0d8", "#d9ccf0", "#f7e2b8", "#c9e9f0", "#f0d3ea"]

        # --- work out how big the floor has to be ----------------------
        mat_cols = 1 if len(mat_names) == 1 else 2
        mat_rows = math.ceil(len(mat_names) / mat_cols)
        cell_w, cell_h = 18, 11          # one mat plus its queue and gap
        club_h = 4
        needed_w = max(2 + mat_cols * cell_w,
                       2 + len(club_names) * 8)
        needed_h = 2 + mat_rows * cell_h + club_h + 2
        floor_w = max(needed_w, width if width else 0)
        floor_h = max(needed_h, height if height else 0)
        venue = cls(floor_w, floor_h)

        # --- mats, packed left to right then top to bottom -------------
        span_w = (floor_w - 2) // mat_cols
        for number, mat_name in enumerate(mat_names):
            col, row = number % mat_cols, number // mat_cols
            x0 = 1 + col * span_w + 1
            x1 = x0 + span_w - 4
            y0 = 2 + row * cell_h
            y1 = y0 + cell_h - 5
            venue.add_area(mat_name, "mat", palette[number % len(palette)],
                           x0, y0, x1, y1)
            venue.add_area(queue_name(mat_name), "queue", queue_colour,
                           x0, y1 + 2, x1, y1 + 2)

        # --- club strip along the bottom -------------------------------
        club_span = (floor_w - 2) // len(club_names)
        club_y1 = floor_h - 2
        club_y0 = club_y1 - club_h + 1
        for number, club_name in enumerate(club_names):
            x0 = 1 + number * club_span
            x1 = x0 + club_span - 2
            venue.add_area(club_name, "club", club_colour,
                           x0, club_y0, x1, club_y1)
        return venue


def queue_name(mat_name):
    """returns the name of the queue area belonging to a mat"""
    return f"{mat_name} queue"


def standing_places(area, count, spacing=2):
    """returns count standing positions inside an area

    Tries the requested spacing first and tightens to neighbouring
    cells if the area is small.  If even that is not enough room the
    positions are cycled, so competitors double up on a cell rather
    than the simulation failing - a small area is a scenario choice,
    not an error.
    """
    if count <= 0:
        return []
    options = [places for places in
               (area.slots(count, spacing=spacing),
                area.slots(count, spacing=1))
               if places]
    places = max(options, key=len) if options else [area.centre()]
    padded = list(places)
    while len(padded) < count:
        padded.extend(places)
    return padded[:count]
