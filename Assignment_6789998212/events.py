#
# events.py - the events run at a Py Kwon Do competition
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# One base class holds everything every event shares: who is eligible,
# calling entrants up, waiting for them to arrive, awarding medal
# points and reporting placings.  Each subclass overrides only the part
# that actually differs - how a round is run and scored - which is the
# polymorphism the assignment asks for.
#
# Sources / self-citation
# -----------------------
# * TeamPatternEvent's synchronised move is my PracTest3 Task 4 group
#   move: one shared (dx, dy) applied through step_change(set_move=...)
#   but only when it keeps every member of the team inside the mat,
#   otherwise nobody moves.
# * The pattern sequences are modelled on Chon-Ji Tul (the Tae Kwon Do
#   pattern linked in the assignment specification), where every move
#   has a direction and an action.
#
import pykwondo as pk

# --- event lifecycle states -------------------------------------------
EVENT_PENDING = "pending"      # scheduled, nobody called yet
EVENT_CALLING = "calling"      # entrants walking to the queue
EVENT_STAGING = "staging"      # entrants walking from queue onto the mat
EVENT_RUNNING = "running"      # rounds are being run
EVENT_FINISHED = "finished"    # results recorded, entrants released

# Named directions a pattern move can be performed in.  y grows
# downwards, matching the venue grid and imshow().
MOVE_VECTORS = {
    "N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
    "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1),
}

# Chon-Ji Tul, trimmed to eight moves - each move is a direction and an
# action, as in the pattern video referenced by the specification.
CHON_JI = [
    ("W", "low block"), ("E", "middle punch"),
    ("E", "low block"), ("W", "middle punch"),
    ("N", "low block"), ("N", "middle punch"),
    ("S", "inner block"), ("S", "middle punch"),
]

# A shorter beginner sequence, used by the junior events.
FOUR_DIRECTION_PUNCH = [
    ("N", "middle punch"), ("E", "low block"),
    ("S", "middle punch"), ("W", "low block"),
]


class Event:
    """
    Base class for everything that happens on a mat.

    Lifecycle (driven one timestep at a time by Competition.step()):

        pending -> calling -> staging -> running -> finished

    `calling` and `staging` both simply wait until every entrant has
    walked to where it was sent, which is why the waiting is written
    once here instead of in each subclass.

    Attributes
    ----------
    name : str
        the event's name, e.g. 'Junior Patterns'
    mat_name : str
        the venue area the event is held on
    min_rank, max_rank : str or None
        inclusive rank band allowed to enter
    min_age, max_age : int or None
        inclusive age band allowed to enter
    difficulty : float
        divides performance scores - a harder event scores lower
    medal_points : tuple
        points awarded for 1st, 2nd, 3rd...
    max_entrants : int or None
        cap on entrants, highest ranked first
    min_entrants : int
        below this the event cannot be held
    state : str
        one of the EVENT_* constants
    entrants : list
        every Competitor called up
    active : list
        entrants still in the event (sparring/breaking eliminate people)
    placings : list
        result dicts, best first, filled in when the event finishes
    held : bool
        False if the event was abandoned for lack of entrants
    round_no : int
        how many rounds have been run

    Methods
    -------
    is_eligible(competitor, ranks)
        rank / age / skill test, the same for every event type
    call_up(pool, venue, ranks)
        selects entrants and sends them to the queue
    update(rng, ranks, venue)
        advances the event's own state machine by one timestep
    advance(rng, ranks, venue)
        run one round - the method each subclass overrides
    ranked_entries(ranks)
        final ordering - the other method each subclass overrides
    """

    # matched against Competitor.skills, and used in scenario files
    type_name = "event"
    # how entrants stand on the mat: 'lines' or 'pairs'
    formation = "lines"

    def __init__(self, name, mat_name, min_rank=None, max_rank=None,
                 min_age=None, max_age=None, difficulty=1.0,
                 medal_points=(5, 3, 1), max_entrants=None, min_entrants=2,
                 require_skill=True):
        """sets up an event that has not been called up yet"""
        self.name = name
        self.mat_name = mat_name
        self.min_rank = min_rank
        self.max_rank = max_rank
        self.min_age = min_age
        self.max_age = max_age
        self.difficulty = difficulty
        self.medal_points = tuple(medal_points)
        self.max_entrants = max_entrants
        self.min_entrants = min_entrants
        self.require_skill = require_skill
        self.state = EVENT_PENDING
        self.entrants = []
        self.active = []
        self.placings = []
        self.held = True
        self.round_no = 0
        self.log = []

    def __str__(self):
        """returns the event name, mat and current state"""
        return f"{self.name} on {self.mat_name} [{self.state}]"

    # --- eligibility ---------------------------------------------------
    def is_eligible(self, competitor, ranks):
        """returns True if this competitor is allowed to enter

        Rank band, age band and trained skill, all optional - an event
        that sets none of them is open to everybody.
        """
        in_rank = ranks.is_between(competitor.rank, self.min_rank,
                                   self.max_rank)
        old_enough = self.min_age is None or competitor.age >= self.min_age
        young_enough = self.max_age is None or competitor.age <= self.max_age
        trained = ((not self.require_skill)
                   or competitor.has_skill(self.type_name))
        return in_rank and old_enough and young_enough and trained

    def eligible_pool(self, competitors, ranks):
        """returns every competitor eligible for this event"""
        return [c for c in competitors if self.is_eligible(c, ranks)]

    def can_be_held(self, competitors, ranks):
        """returns True if enough eligible competitors exist"""
        return len(self.eligible_pool(competitors, ranks)) >= self.min_entrants

    # --- calling up ----------------------------------------------------
    def call_up(self, competitors, venue, ranks):
        """locks in the entrants and sends them to the mat's queue

        Only competitors that are free are taken, which is the rule that
        stops a competitor being pulled off one mat by an event starting
        on another.  Competition only calls an event up when all of its
        eligible competitors are free, so in practice this takes the
        whole eligible pool.

        Returns
        -------
        list
            the competitors called up
        """
        pool = [c for c in self.eligible_pool(competitors, ranks)
                if c.is_free()]
        pool.sort(key=lambda c: (-ranks.index(c.rank), c.comp_id))
        chosen = (pool if self.max_entrants is None
                  else pool[:self.max_entrants])
        if len(chosen) < self.min_entrants:
            # Not enough people free *right now* - stay pending and try
            # again on a later timestep.  An event that can never be
            # filled at all is abandoned by Competition instead, so a
            # busy mat is never mistaken for an impossible event.
            return []
        queue = venue.area(pk.queue_name(self.mat_name))
        places = pk.standing_places(queue, len(chosen))
        for competitor, place in zip(chosen, places):
            competitor.assign_event(self)
            competitor.state = pk.STATE_TRAVELLING
            competitor.set_target(place)
        self.entrants = chosen
        self.active = list(chosen)
        self.state = EVENT_CALLING
        self.log.append(f"{self.name}: called up {len(chosen)} entrants")
        return chosen

    def everyone_arrived(self):
        """returns True when every active entrant is on its target cell"""
        return all(c.at_target() for c in self.active)

    # --- the event's own state machine ---------------------------------
    def update(self, rng, ranks, venue):
        """advances this event by one timestep

        Called every timestep by Competition while the event is not
        finished.  Returns True on the timestep the event finishes.
        """
        if self.state == EVENT_CALLING and self.everyone_arrived():
            self.start_staging(venue)
        elif self.state == EVENT_STAGING and self.everyone_arrived():
            self.start_running()
        elif self.state == EVENT_RUNNING:
            self.round_no += 1
            if self.advance(rng, ranks, venue):
                self.finish(ranks)
                return True
        return False

    def start_staging(self, venue):
        """walks the entrants from the queue onto their mat positions"""
        mat = venue.area(self.mat_name)
        for competitor, place in zip(self.active, self.mat_positions(mat)):
            competitor.state = pk.STATE_STAGING
            competitor.set_target(place)
        self.state = EVENT_STAGING

    def start_running(self):
        """everyone is in position - the event begins"""
        for competitor in self.active:
            competitor.state = pk.STATE_COMPETING
            competitor.clear_target()
        self.state = EVENT_RUNNING
        self.round_no = 0
        self.log.append(f"{self.name}: under way with "
                        f"{len(self.active)} entrants")

    def mat_positions(self, mat):
        """returns where each active entrant stands on the mat

        Overridden by events whose competitors need a special formation
        (sparring pairs face each other, teams stand in blocks).
        """
        return pk.standing_places(mat, len(self.active), spacing=2)

    def advance(self, rng, ranks, venue):
        """runs one round - every event type does this differently

        Returns
        -------
        bool
            True when the event has run its last round
        """
        raise NotImplementedError("each event type runs its own rounds")

    def ranked_entries(self, ranks):
        """returns the final order, best first

        Returns
        -------
        list
            (label, score, [competitors sharing the placing]) tuples
        """
        raise NotImplementedError("each event type decides its own order")

    # --- finishing -----------------------------------------------------
    def finish(self, ranks):
        """records placings, awards medal points and releases everyone"""
        ordered = self.ranked_entries(ranks)
        for place, (label, score, members) in enumerate(ordered, start=1):
            points = (self.medal_points[place - 1]
                      if place <= len(self.medal_points) else 0)
            self.placings.append({"place": place, "label": label,
                                  "score": round(score, 1), "points": points,
                                  "members": members})
            for competitor in members:
                competitor.record_placing(self.name, place,
                                          round(score, 1), points)
        for competitor in self.entrants:
            competitor.release()
        self.state = EVENT_FINISHED
        winner = self.placings[0]["label"] if self.placings else "nobody"
        self.log.append(f"{self.name}: finished, won by {winner}")

    def is_finished(self):
        """returns True once the event is over"""
        return self.state == EVENT_FINISHED

    def eliminate(self, competitor, reason=""):
        """takes a competitor out of the event and sends it home early"""
        if competitor in self.active:
            self.active.remove(competitor)
        competitor.release()
        if reason:
            self.log.append(f"{self.name}: {competitor.get_name()} "
                            f"out - {reason}")

    def winner(self):
        """returns the label of the winner, or None if not decided"""
        return self.placings[0]["label"] if self.placings else None

    def summary(self):
        """returns the result table for this event as a list of lines"""
        if not self.held:
            return [f"{self.name}: not held (too few eligible competitors)"]
        band = self.rank_band_text()
        lines = [f"{self.name} - {self.type_name} on {self.mat_name} ({band})"]
        lines.extend(
            f"    {p['place']}. {p['label']:<28} score {p['score']:>6.1f}"
            f"   {p['points']} pts" for p in self.placings)
        return lines

    def rank_band_text(self):
        """returns a readable description of who could enter"""
        low = self.min_rank if self.min_rank else "any"
        high = self.max_rank if self.max_rank else "any"
        ages = ""
        if self.min_age is not None or self.max_age is not None:
            ages = f", age {self.min_age or 0}-{self.max_age or 99}"
        return f"{low} to {high}{ages}"


class PatternEvent(Event):
    """
    Individual patterns: every entrant performs the same sequence of
    moves at the same time and is scored on accuracy.

    One move of the sequence is performed per timestep.  Each move has a
    direction and an action, so competitors visibly turn and step
    through the pattern on the mat, and the score for the move is the
    competitor's performance for that timestep.
    """

    type_name = "pattern"

    def __init__(self, name, mat_name, sequence=None, **kwargs):
        """sets up a pattern event with its move sequence"""
        super().__init__(name, mat_name, **kwargs)
        self.sequence = list(sequence) if sequence else list(CHON_JI)
        self.accuracy = {}

    def start_running(self):
        """everyone faces the judges before the first move"""
        super().start_running()
        self.accuracy = {c.comp_id: 0.0 for c in self.active}
        for competitor in self.active:
            competitor.face((0, -1))

    def advance(self, rng, ranks, venue):
        """performs the next move of the pattern and scores it"""
        direction, action = self.sequence[self.round_no - 1]
        vector = MOVE_VECTORS[direction]
        mat = venue.area(self.mat_name)
        for competitor in self.active:
            competitor.face(vector)
            step_to = (competitor.get_pos()[0] + vector[0],
                       competitor.get_pos()[1] + vector[1])
            if mat.contains(step_to) and venue.is_walkable(step_to):
                competitor.step_change(set_move=vector, venue=venue)
            self.accuracy[competitor.comp_id] += competitor.performance(
                ranks, rng, self.difficulty)
        self.log.append(f"{self.name}: move {self.round_no} - "
                        f"{direction} {action}")
        return self.round_no >= len(self.sequence)

    def ranked_entries(self, ranks):
        """orders entrants by mean accuracy over the whole pattern"""
        moves = max(1, len(self.sequence))
        scored = [(c, self.accuracy[c.comp_id] / moves) for c in self.active]
        scored.sort(key=lambda pair: -pair[1])
        return [(f"{c.get_name()} ({c.get_club()})", score, [c])
                for c, score in scored]


class SparringEvent(Event):
    """
    Sparring: entrants are paired against the nearest rank to them and
    fight a single-elimination bracket, one round of the whole bracket
    per timestep.

    An odd number of entrants means somebody gets a bye that round and
    goes through without fighting, which is what a real draw does.
    """

    type_name = "sparring"
    formation = "pairs"

    def __init__(self, name, mat_name, **kwargs):
        """sets up a sparring event"""
        kwargs.setdefault("min_entrants", 2)
        super().__init__(name, mat_name, **kwargs)
        self.pairs = []
        self.byes = []
        self.knocked_out = []      # (competitor, round eliminated, score)
        self.best_score = {}

    def pair_up(self, ranks):
        """pairs the remaining competitors by nearest rank

        Sorting by rank first means each pair is as close in belt as the
        draw allows.  With an odd number the last competitor in the
        order gets the bye.
        """
        order = sorted(self.active,
                       key=lambda c: (ranks.index(c.rank), -c.form))
        pairs = [(order[i], order[i + 1]) for i in range(0, len(order) - 1, 2)]
        bye = [order[-1]] if len(order) % 2 == 1 else []
        return pairs, bye

    def start_running(self):
        """draws the first round of the bracket"""
        super().start_running()
        self.best_score = {c.comp_id: 0.0 for c in self.active}

    def mat_positions(self, mat):
        """stands each pair two cells apart, facing each other"""
        pair_count = (len(self.active) + 1) // 2
        places = []
        for left, right in mat.pair_slots(pair_count):
            places.extend([left, right])
        if len(places) < len(self.active):
            places = pk.standing_places(mat, len(self.active), spacing=2)
        return places[:len(self.active)]

    def advance(self, rng, ranks, venue):
        """fights one round of the bracket

        Both competitors in a pair score an attempt; the higher score
        wins the bout and goes through, the loser is eliminated and
        walks back to its club area straight away.
        """
        self.pairs, self.byes = self.pair_up(ranks)
        losers = []
        for red, blue in self.pairs:
            red.face_towards(blue.get_pos())
            blue.face_towards(red.get_pos())
            red_score = red.performance(ranks, rng, self.difficulty)
            blue_score = blue.performance(ranks, rng, self.difficulty)
            self.best_score[red.comp_id] = max(
                self.best_score[red.comp_id], red_score)
            self.best_score[blue.comp_id] = max(
                self.best_score[blue.comp_id], blue_score)
            loser = blue if red_score >= blue_score else red
            winner = red if loser is blue else blue
            losers.append(loser)
            self.log.append(
                f"{self.name}: round {self.round_no} - "
                f"{winner.get_name()} beat "
                f"{loser.get_name()} ({max(red_score, blue_score):.1f} v "
                f"{min(red_score, blue_score):.1f})")
        for competitor in self.byes:
            self.log.append(f"{self.name}: round {self.round_no} - "
                            f"{competitor.get_name()} has a bye")
        for loser in losers:
            self.knocked_out.append((loser, self.round_no,
                                     self.best_score[loser.comp_id]))
            self.eliminate(loser, f"knocked out in round {self.round_no}")
        for competitor in self.active:
            self.restage(competitor, venue)
        return len(self.active) <= 1

    def restage(self, competitor, venue):
        """moves a survivor back towards the middle of the mat"""
        mat = venue.area(self.mat_name)
        competitor.set_target(mat.centre())
        competitor.step_change(venue=venue)
        competitor.clear_target()

    def ranked_entries(self, ranks):
        """orders by how far each competitor got in the bracket"""
        entries = []
        if self.active:
            champion = self.active[0]
            entries.append((f"{champion.get_name()} ({champion.get_club()})",
                            self.best_score[champion.comp_id], [champion]))
        beaten = sorted(self.knocked_out,
                        key=lambda item: (-item[1], -item[2]))
        entries.extend((f"{c.get_name()} ({c.get_club()})", score, [c])
                       for c, _, score in beaten)
        return entries


class TeamPatternEvent(Event):
    """
    Group patterns: each club enters a team which performs a sequence
    together, and is scored on both accuracy and how well synchronised
    the team is.

    The whole team is given one shared (dx, dy) move each round, which
    is only applied if it keeps every member of that team on the mat -
    the all-or-nothing group move from PracTest3 Task 4.
    """

    type_name = "team_pattern"

    def __init__(self, name, mat_name, sequence=None, team_size=3, **kwargs):
        """sets up a team event with its sequence and minimum team size"""
        kwargs.setdefault("min_entrants", 2)
        super().__init__(name, mat_name, **kwargs)
        self.sequence = (list(sequence) if sequence
                         else list(FOUR_DIRECTION_PUNCH))
        self.team_size = team_size
        self.teams = {}
        self.accuracy = {}
        self.worst_gap = {}

    def can_be_held(self, competitors, ranks):
        """returns True only if at least two clubs can field a team"""
        pool = self.eligible_pool(competitors, ranks)
        return len(self.build_teams(pool)) >= 2

    def build_teams(self, pool):
        """groups a pool of competitors into full-sized club teams"""
        by_club = {}
        for competitor in pool:
            by_club.setdefault(competitor.get_club(), []).append(competitor)
        return {club: members[:self.team_size]
                for club, members in sorted(by_club.items())
                if len(members) >= self.team_size}

    def call_up(self, competitors, venue, ranks):
        """calls up whole club teams only, dropping clubs that are short"""
        pool = [c for c in self.eligible_pool(competitors, ranks)
                if c.is_free()]
        teams = self.build_teams(pool)
        if len(teams) < 2:
            # As above: too few teams free this timestep, so wait.
            return []
        self.teams = teams
        chosen = [c for members in teams.values() for c in members]
        queue = venue.area(pk.queue_name(self.mat_name))
        places = pk.standing_places(queue, len(chosen))
        for competitor, place in zip(chosen, places):
            competitor.assign_event(self)
            competitor.state = pk.STATE_TRAVELLING
            competitor.set_target(place)
        self.entrants = chosen
        self.active = list(chosen)
        self.state = EVENT_CALLING
        self.log.append(f"{self.name}: called up {len(teams)} teams "
                        f"({len(chosen)} competitors)")
        return chosen

    def mat_positions(self, mat):
        """gives each team its own block of the mat, side by side"""
        team_count = max(1, len(self.teams))
        span = max(2, mat.width() // team_count)
        places = []
        for number, members in enumerate(self.teams.values()):
            left = mat.x0 + number * span
            row = mat.y0 + 1
            places.extend([(min(left + 2 * i, mat.x1), row)
                           for i in range(len(members))])
        return places

    def start_running(self):
        """resets the accuracy and synchronisation tallies"""
        super().start_running()
        self.accuracy = {c.comp_id: 0.0 for c in self.active}
        self.worst_gap = {club: 0.0 for club in self.teams}

    def advance(self, rng, ranks, venue):
        """performs one move of the sequence, team by team"""
        direction, action = self.sequence[self.round_no - 1]
        vector = MOVE_VECTORS[direction]
        mat = venue.area(self.mat_name)
        for club, members in self.teams.items():
            on_mat = [c for c in members if c in self.active]
            # PracTest3 Task 4: check the shared move for EVERY member
            # before letting anybody take it.
            move_is_safe = all(
                mat.contains((c.get_pos()[0] + vector[0],
                              c.get_pos()[1] + vector[1])) for c in on_mat)
            scores = []
            for competitor in on_mat:
                competitor.face(vector)
                if move_is_safe:
                    competitor.step_change(set_move=vector, venue=venue)
                score = competitor.performance(ranks, rng, self.difficulty)
                self.accuracy[competitor.comp_id] += score
                scores.append(score)
            if scores:
                gap = max(scores) - min(scores)
                self.worst_gap[club] = max(self.worst_gap[club], gap)
        self.log.append(f"{self.name}: move {self.round_no} - "
                        f"{direction} {action}")
        return self.round_no >= len(self.sequence)

    def ranked_entries(self, ranks):
        """orders clubs by mean accuracy minus a synchronisation penalty"""
        moves = max(1, len(self.sequence))
        entries = []
        for club, members in self.teams.items():
            total = sum(self.accuracy[c.comp_id] for c in members)
            mean = total / (len(members) * moves)
            entries.append((f"{club} team", mean - self.worst_gap[club] / 2.0,
                            list(members)))
        entries.sort(key=lambda entry: -entry[1])
        return entries


class BreakingEvent(Event):
    """
    Specialist technique: power breaking.  Every round the board count
    goes up by one and everybody still in has an attempt; anyone who
    fails is out and walks back to their club.  Placing is by boards
    broken, then by the quality of the last successful attempt.

    Restricted to the senior belts by the scenario, because breaking
    boards is not a beginner activity.
    """

    type_name = "breaking"

    def __init__(self, name, mat_name, start_boards=1, max_boards=6,
                 board_difficulty=9.0, **kwargs):
        """sets up a breaking event and how hard each board is"""
        super().__init__(name, mat_name, **kwargs)
        self.start_boards = start_boards
        self.max_boards = max_boards
        self.board_difficulty = board_difficulty
        self.boards = {}
        self.last_score = {}

    def start_running(self):
        """everybody starts on zero boards, facing the boards"""
        super().start_running()
        self.boards = {c.comp_id: 0 for c in self.active}
        self.last_score = {c.comp_id: 0.0 for c in self.active}
        for competitor in self.active:
            competitor.face((0, -1))

    def threshold(self, boards):
        """returns the score needed to break this many boards"""
        return 30.0 + self.board_difficulty * boards

    def advance(self, rng, ranks, venue):
        """one attempt each, at one more board than last round"""
        boards = self.start_boards + self.round_no - 1
        needed = self.threshold(boards)
        failures = []
        for competitor in self.active:
            score = competitor.performance(ranks, rng, self.difficulty)
            self.last_score[competitor.comp_id] = score
            if score >= needed:
                self.boards[competitor.comp_id] = boards
                self.log.append(f"{self.name}: {competitor.get_name()} broke "
                                f"{boards} board(s) ({score:.1f})")
            else:
                failures.append(competitor)
                self.log.append(
                    f"{self.name}: {competitor.get_name()} failed at "
                    f"{boards} board(s) ({score:.1f} < {needed:.1f})")
        for competitor in failures:
            self.eliminate(competitor, f"failed at {boards} boards")
        return len(self.active) <= 1 or boards >= self.max_boards

    def ranked_entries(self, ranks):
        """orders everyone by boards broken, then by last score"""
        everyone = list(self.entrants)
        everyone.sort(key=lambda c: (-self.boards.get(c.comp_id, 0),
                                     -self.last_score.get(c.comp_id, 0.0)))
        return [(f"{c.get_name()} ({c.get_club()}) - "
                 f"{self.boards.get(c.comp_id, 0)} boards",
                 float(self.boards.get(c.comp_id, 0)) * 10
                 + self.last_score.get(c.comp_id, 0.0) / 10, [c])
                for c in everyone]


# Event type name -> class, used by the scenario loader so that scenario
# files name event types in text without the loader needing an if-chain.
EVENT_TYPES = {
    PatternEvent.type_name: PatternEvent,
    SparringEvent.type_name: SparringEvent,
    TeamPatternEvent.type_name: TeamPatternEvent,
    BreakingEvent.type_name: BreakingEvent,
}


def make_event(config):
    """builds an Event from a scenario dictionary

    Parameters
    ----------
    config : dict
        must have 'type', 'name' and 'mat'; every other key is passed
        to the event class as a keyword argument

    Returns
    -------
    Event
        an instance of the matching Event subclass
    """
    settings = dict(config)
    type_name = settings.pop("type", None)
    if type_name not in EVENT_TYPES:
        raise ValueError(f"unknown event type {type_name!r}, "
                         f"expected one of {sorted(EVENT_TYPES)}")
    name = settings.pop("name", None)
    mat = settings.pop("mat", None)
    if not name or not mat:
        raise ValueError(f"event {type_name!r} needs both a 'name' "
                         f"and a 'mat'")
    if "sequence" in settings:
        settings["sequence"] = [tuple(move) for move in settings["sequence"]]
    if "medal_points" in settings:
        settings["medal_points"] = tuple(settings["medal_points"])
    return EVENT_TYPES[type_name](name, mat, **settings)
