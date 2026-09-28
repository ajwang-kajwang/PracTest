#
# competition.py - runs a whole Py Kwon Do competition
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# Competition owns the venue, the clubs, the competitors and the
# schedule of events, and advances all of them one timestep at a time.
# It is the object that decides WHEN an event may start; the event
# itself decides what happens once it has.
#
# Sources / self-citation
# -----------------------
# * The timestep loop is the PracTest3 Task 3/4 simulation loop: one
#   pass per timestep, everybody's step_change() called once, then the
#   plot redrawn.  Nothing here loops until a condition becomes true -
#   each timestep simply CHECKS the arrival/finish conditions, which is
#   why no while True/break is needed anywhere.
# * The per-timestep history arrays follow PracTest2's approach of
#   recording every step into NumPy arrays and plotting them afterwards.
#
import random

import numpy as np

import events as ev
import pykwondo as pk


class Competition:
    """
    A whole competition: a venue, some clubs of competitors, and a
    schedule of events run on the venue's mats.

    Scheduling rule
    ---------------
    An event may start when
      (a) its mat is free,
      (b) fewer than max_parallel events are already live, and
      (c) EVERY competitor eligible for it is free.

    Rule (c) is what makes overlapping eligibility safe.  A competitor
    is locked to one event at a time, so without it an event starting
    on mat B would drag entrants off mat A, and then neither event
    would ever see all its entrants arrive - both would stall with
    empty results and no error message.  With it, two events run in
    parallel exactly when their eligible pools do not overlap (typically
    different rank bands), which is how a real competition uses two
    mats.

    Attributes
    ----------
    name : str
        the competition's name, used in titles and reports
    venue : Venue
    ranks : RankSystem
    clubs : dict
        club name -> Club
    competitors : list
        every Competitor taking part
    events : list
        the schedule, in the order events should be tried
    max_parallel : int
        how many events may be live at once
    step_no : int
        timesteps run so far
    history : list
        one dict per timestep, for after-the-fact plots
    log : list
        commentary lines, newest last
    """

    def __init__(self, name, venue, ranks, clubs, competitors, events,
                 rng=None, max_parallel=2):
        """assembles a competition ready to run"""
        self.name = name
        self.venue = venue
        self.ranks = ranks
        self.clubs = clubs
        self.competitors = competitors
        self.events = events
        self.rng = rng if rng else random.Random()
        self.max_parallel = max(1, max_parallel)
        self.step_no = 0
        self.history = []
        self.log = []
        self.finished_order = []

    def __str__(self):
        """returns a one-line description of the competition"""
        return (f"{self.name}: {len(self.competitors)} competitors, "
                f"{len(self.clubs)} clubs, {len(self.events)} events "
                f"at step {self.step_no}")

    # --- scheduling ----------------------------------------------------
    def live_events(self):
        """returns the events currently calling, staging or running"""
        return [event for event in self.events
                if event.state in (ev.EVENT_CALLING, ev.EVENT_STAGING,
                                   ev.EVENT_RUNNING)]

    def pending_events(self):
        """returns the events that have not started yet"""
        return [event for event in self.events
                if event.state == ev.EVENT_PENDING]

    def pool_is_free(self, event):
        """returns True if every competitor eligible for an event is free"""
        pool = event.eligible_pool(self.competitors, self.ranks)
        return bool(pool) and all(competitor.is_free() for competitor in pool)

    def events_to_start(self):
        """returns the pending events that may start this timestep

        Works down the schedule in order, keeping track of the mats,
        the parallel slots AND the competitors that the events already
        chosen this timestep are about to claim.  Tracking the claimed
        competitors matters: two events whose eligible pools overlap
        both look startable when each is checked on its own, because
        nobody is locked until call_up() runs a moment later.  Without
        this the second event calls up an empty entry list and is never
        held at all.
        """
        busy_mats = {event.mat_name for event in self.live_events()}
        free_slots = self.max_parallel - len(busy_mats)
        claimed = set()
        starting = []
        for event in self.pending_events():
            pool = event.eligible_pool(self.competitors, self.ranks)
            everyone_free = bool(pool) and all(c.is_free() for c in pool)
            wanted_by_another = any(c.comp_id in claimed for c in pool)
            if (len(starting) < free_slots and event.mat_name not in busy_mats
                    and everyone_free and not wanted_by_another):
                starting.append(event)
                busy_mats.add(event.mat_name)
                claimed.update(c.comp_id for c in pool)
        return starting

    def abandon_impossible_events(self):
        """finishes off any event that can never gather enough entrants

        Checked against the whole roster, not just who is free, so an
        event is only abandoned when the competitors simply do not
        exist - otherwise it would block the schedule forever.
        """
        doomed = [event for event in self.pending_events()
                  if not event.can_be_held(self.competitors, self.ranks)]
        for event in doomed:
            event.held = False
            event.state = ev.EVENT_FINISHED
            self.note(f"{event.name} abandoned - not enough "
                      f"eligible competitors")

    # --- one timestep --------------------------------------------------
    def step(self):
        """advances the whole simulation by one timestep"""
        self.step_no += 1
        self.abandon_impossible_events()
        for event in self.events_to_start():
            called = event.call_up(self.competitors, self.venue, self.ranks)
            self.note(f"{event.name} called up {len(called)} competitors "
                      f"to {event.mat_name}")
        for event in self.live_events():
            if event.update(self.rng, self.ranks, self.venue):
                self.settle(event)
        self.move_everyone()
        self.record_history()
        return self.is_complete()

    def move_everyone(self):
        """gives every competitor its one step_change() for the timestep

        Competitors on a mat have no target, so their step_change()
        does nothing - their event moves them instead.  Anyone walking
        somewhere takes one Moore step towards it, barriers checked.
        """
        for competitor in self.competitors:
            competitor.step_change(venue=self.venue)
            arrived = competitor.at_target()
            if competitor.state == pk.STATE_TRAVELLING and arrived:
                competitor.state = pk.STATE_QUEUED
            elif competitor.state == pk.STATE_RETURNING and arrived:
                competitor.state = pk.STATE_WAITING
                competitor.clear_target()
            elif competitor.state == pk.STATE_WAITING:
                # idle competitors shadow-box: they turn on the spot
                competitor.face(self.rng.choice(list(pk.COMPASS)))

    def settle(self, event):
        """records an event's results against competitors and clubs"""
        self.finished_order.append(event)
        for placing in event.placings:
            for competitor in placing["members"]:
                club = self.clubs.get(competitor.get_club())
                if club:
                    club.points += placing["points"]
        self.note(f"{event.name} finished - won by {event.winner()}")

    def record_history(self):
        """stores this timestep's headline numbers for later plots"""
        self.history.append({
            "step": self.step_no,
            "competing": sum(1 for c in self.competitors
                             if c.state == pk.STATE_COMPETING),
            "walking": sum(1 for c in self.competitors
                           if c.state in (pk.STATE_TRAVELLING,
                                          pk.STATE_STAGING,
                                          pk.STATE_RETURNING)),
            "waiting": sum(1 for c in self.competitors
                           if c.state == pk.STATE_WAITING),
            "events_live": len(self.live_events()),
            "events_done": sum(1 for e in self.events if e.is_finished()),
            "club_points": {name: club.points
                            for name, club in self.clubs.items()},
        })

    def note(self, line):
        """adds a line of commentary to the competition log"""
        self.log.append(f"[t={self.step_no:3d}] {line}")

    # --- running the whole thing ---------------------------------------
    def is_complete(self):
        """returns True when every event is done and everyone is home"""
        return (all(event.is_finished() for event in self.events)
                and all(c.state == pk.STATE_WAITING for c in self.competitors))

    def run(self, max_steps, view=None, on_step=None):
        """runs the competition until it finishes or runs out of steps

        The loop condition does the work that a `while True` with a
        `break` would otherwise do: it stops when the competition is
        complete, or when the timestep budget is spent.

        Parameters
        ----------
        max_steps : int
            timestep budget
        view : SimView, optional
            live plot to update each timestep
        on_step : callable, optional
            called with (competition) after each timestep, for printing

        Returns
        -------
        bool
            True if the competition finished inside the budget
        """
        while self.step_no < max_steps and not self.is_complete():
            self.step()
            if view is not None:
                view.update(self)
            if on_step is not None:
                on_step(self)
        return self.is_complete()

    # --- results --------------------------------------------------------
    def standings(self):
        """returns competitors ordered by points, best first"""
        golds = lambda c: sum(1 for _, place, _ in c.placings if place == 1)
        return sorted(self.competitors,
                      key=lambda c: (-c.points, -golds(c), c.get_name()))

    def club_standings(self):
        """returns (club, points, golds) tuples ordered by points

        A gold is one EVENT won by the club, not one competitor with a
        first place - otherwise a three-member team win would count as
        three golds.
        """
        rows = []
        for club in self.clubs.values():
            won = {name for member in club.members
                   for name, place, _ in member.placings if place == 1}
            rows.append((club, club.points, len(won)))
        rows.sort(key=lambda row: (-row[1], -row[2], row[0].name))
        return rows

    def held_events(self):
        """returns the events that actually took place"""
        return [event for event in self.events
                if event.held and event.placings]

    def history_array(self):
        """returns the per-timestep state counts as a NumPy array

        Columns are step, competing, walking, waiting, events live and
        events done - one row per timestep, in the same style as the
        PracTest2 walker arrays.
        """
        if not self.history:
            return np.zeros((0, 6), dtype=int)
        return np.array([[row["step"], row["competing"], row["walking"],
                          row["waiting"], row["events_live"],
                          row["events_done"]]
                         for row in self.history], dtype=int)

    def club_points_array(self):
        """returns club point totals per timestep as a NumPy array

        Returns
        -------
        names : list
            club names, one per column
        table : numpy.ndarray
            shape (timesteps, clubs)
        """
        names = sorted(self.clubs)
        if not self.history:
            return names, np.zeros((0, len(names)), dtype=int)
        table = np.array([[row["club_points"].get(name, 0) for name in names]
                          for row in self.history], dtype=int)
        return names, table
