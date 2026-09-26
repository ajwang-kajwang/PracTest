#
# visualise.py - the live plot of a running competition
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# One window, redrawn each timestep: a map of the venue with every
# competitor on it, a rank chart and the running club scores, plus a
# line of commentary about what each mat is doing.
#
# Sources / self-citation
# -----------------------
# * The single-window animation is exactly the fix from my PracTest3
#   Task 3: plt.ion() once, then ONE plt.figure() created outside the
#   loop, and each timestep plt.clf() followed by rebuilding the axes
#   on that same figure.  Calling plt.subplots() inside the loop (as
#   the given training.py does) opens a brand new window every
#   timestep - reference_solutions/task3_v1_naive.py in PracTest3 shows
#   the figure numbers climbing 1, 2, 3 ... while it runs.
# * The floor is drawn with imshow() and the competitors with
#   scatter(), coloured by rank, as in PracTest3 Tasks 1-4.  The colour
#   map is a ListedColormap instead of 'Greys' so each area of the
#   venue gets its own colour.
# * get_namelist() and get_ranklist() (given code) build the rank
#   chart, as in PracTest3 Task 3.
#
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

import pykwondo as pk
from characters import get_namelist, get_ranklist

# Marker shape per competitor state, so the map shows what everyone is
# doing as well as where they are.
STATE_MARKERS = {
    pk.STATE_WAITING: "o",
    pk.STATE_TRAVELLING: ">",
    pk.STATE_QUEUED: "s",
    pk.STATE_STAGING: "^",
    pk.STATE_COMPETING: "*",
    pk.STATE_RETURNING: "v",
}
STATE_SIZES = {
    pk.STATE_COMPETING: 190,
    pk.STATE_QUEUED: 70,
}
DEFAULT_SIZE = 90
CROWDED_SIZE = 55       # smaller dots once the venue gets busy

# Above this many competitors the per-competitor rank chart becomes
# unreadable, so the panel switches to counts per rank instead.
NAME_CHART_LIMIT = 14

# Smallest pause handed to plt.pause() - see SimView.update().
MIN_PAUSE = 0.001


class SimView:
    """
    The live dashboard for a Competition.

    Attributes
    ----------
    fig : matplotlib.figure.Figure
        the one and only window, created once
    pause : float
        seconds to pause after each redraw
    interactive : bool
        False for batch runs, where nothing is shown on screen

    Methods
    -------
    update(competition)
        redraw the window for the current timestep
    save(path)
        write the current frame to a file
    close()
        close the window
    """

    def __init__(self, competition, pause=0.35, interactive=True,
                 figsize=(14, 8.5)):
        """creates the single figure the whole run is drawn on"""
        self.pause = pause
        self.interactive = interactive
        if interactive:
            plt.ion()
        # Created ONCE, outside the timestep loop (PracTest3 Task 3).
        self.fig = plt.figure(figsize=figsize)
        self.cmap = ListedColormap(competition.venue.colour_table())
        self.top_code = len(competition.venue.colour_table()) - 1

    def update(self, competition):
        """redraws every panel for the current timestep"""
        plt.clf()
        # The axes are rebuilt on the SAME figure each timestep - this
        # is fig.add_gridspec()/add_subplot(), not plt.subplots(), which
        # would open a new window (PracTest3 Task 3).
        grid = self.fig.add_gridspec(2, 3, height_ratios=[1.7, 1.0])
        ax_map = self.fig.add_subplot(grid[0, :])
        ax_rank = self.fig.add_subplot(grid[1, 0])
        ax_points = self.fig.add_subplot(grid[1, 1])
        ax_status = self.fig.add_subplot(grid[1, 2])

        self.draw_venue(ax_map, competition)
        self.draw_rank_chart(ax_rank, competition)
        self.draw_club_points(ax_points, competition)
        self.draw_status(ax_status, competition)

        self.fig.suptitle(f"{competition.name} - "
                          f"timestep {competition.step_no}",
                          fontsize=14)
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])
        if self.interactive:
            # never pause for exactly zero: plt.pause(0) hands control
            # to the backend's event loop with no timeout, which on
            # some backends never comes back and the run appears to
            # freeze.  A tiny pause still lets the window redraw.
            plt.pause(max(MIN_PAUSE, self.pause))
        return self.fig

    def draw_venue(self, ax, competition):
        """draws the floor, the areas and everybody standing on them"""
        venue = competition.venue
        ax.imshow(np.array(venue.grid()), cmap=self.cmap,
                  vmin=0, vmax=self.top_code, interpolation="nearest")

        # area labels, so it is obvious which mat is which.  Club
        # labels sit along the bottom edge of their area, where the
        # competitors standing in it will not cover them up.
        for area in venue.areas.values():
            if area.kind == "mat":
                ax.text(area.centre()[0], area.y0 + 0.4, area.name,
                        ha="center", va="top", fontsize=8, color="#333333")
            elif area.kind == "club":
                # written on the wall below the area, like a club
                # banner, so the competitors standing in the area do
                # not cover it up
                ax.text(area.centre()[0], area.y1 + 0.9, area.name,
                        ha="center", va="center", fontsize=7.5,
                        color="white")

        # competitors, grouped by state so each state gets its own
        # marker shape, and coloured by rank.  The black edge keeps
        # White belts visible on a pale floor.
        crowded = len(competition.competitors) > 20
        for state, marker in STATE_MARKERS.items():
            group = [c for c in competition.competitors
                     if c.get_state() == state]
            if group:
                ax.scatter([c.get_pos()[0] for c in group],
                           [c.get_pos()[1] for c in group],
                           marker=marker,
                           s=STATE_SIZES.get(state,
                                             CROWDED_SIZE if crowded
                                             else DEFAULT_SIZE),
                           color=[competition.ranks.colour(c.get_rank())
                                  for c in group],
                           edgecolors="black", linewidths=0.7, zorder=3)

        # which way everyone is facing
        ax.quiver([c.get_pos()[0] for c in competition.competitors],
                  [c.get_pos()[1] for c in competition.competitors],
                  [c.get_direction()[0] for c in competition.competitors],
                  [-c.get_direction()[1] for c in competition.competitors],
                  color="#222222", width=0.0035, scale=38, zorder=4)

        ax.set_title("Venue - marker shape shows state, colour shows rank")
        ax.set_xticks([])
        ax.set_yticks([])
        # outside the axes, in the margin imshow's fixed aspect leaves,
        # so it never sits on top of a mat label
        ax.legend(handles=state_legend(), loc="upper left",
                  bbox_to_anchor=(1.01, 1.0), fontsize=7, framealpha=0.9)

    def draw_rank_chart(self, ax, competition):
        """draws the rank panel - per competitor, or counts if crowded"""
        ranks = competition.ranks
        competitors = competition.competitors
        if len(competitors) <= NAME_CHART_LIMIT:
            # PracTest3 Task 3 chart, built with the given helpers.
            names = get_namelist(competitors)
            colours, numbers = get_ranklist(competitors, ranks.names())
            # +1 so a White belt (rank number 0) still draws a bar -
            # the "where did my White belts go?" problem from PracTest3.
            ax.barh(names, [number + 1 for number in numbers],
                    color=colours, edgecolor="black")
            ax.set_xlabel("rank level (1 = lowest belt)")
            ax.set_title("Competitor ranks")
        else:
            counts = {name: sum(1 for c in competitors if c.get_rank() == name)
                      for name in ranks.names()}
            ax.barh(list(counts), list(counts.values()),
                    color=ranks.colours(), edgecolor="black")
            ax.set_xlabel("competitors")
            ax.set_title("Competitors at each rank")
        ax.tick_params(labelsize=7)

    def draw_club_points(self, ax, competition):
        """draws the live club scoreboard"""
        standings = competition.club_standings()
        names = [club.name for club, _, _ in standings]
        points = [total for _, total, _ in standings]
        ax.barh(names, points, color="#e0a458", edgecolor="black")
        ax.invert_yaxis()
        ax.set_xlabel("medal points")
        ax.set_title("Club scoreboard")
        ax.tick_params(labelsize=7)
        ax.set_xlim(0, max(points + [1]) * 1.15)
        for position, total in enumerate(points):
            ax.text(total + 0.1, position, str(total), va="center", fontsize=7)

    def draw_status(self, ax, competition):
        """writes what each mat is doing into its own panel"""
        ax.axis("off")
        ax.set_title("On the mats")
        ax.text(0.0, 1.0, status_text(competition), fontsize=7.5,
                family="monospace", va="top", ha="left",
                transform=ax.transAxes)

    def save(self, path):
        """saves the current frame to an image file"""
        self.fig.savefig(path, dpi=110)
        return path

    def close(self):
        """closes the window"""
        plt.close(self.fig)


def state_legend():
    """returns legend handles explaining the marker shapes"""
    return [Line2D([], [], color="none", marker=marker,
                   markeredgecolor="black",
                   markerfacecolor="#cccccc", markersize=7, label=state)
            for state, marker in STATE_MARKERS.items()]


def status_text(competition):
    """returns a few lines describing what each mat is doing right now"""
    lines = []
    for event in competition.events:
        leader = event.winner() if event.placings else "-"
        state = event.state if event.held else "not held"
        lines.append(f"{shorten(event.name, 20):<20} {event.mat_name:<6} "
                     f"{state:<9}")
        lines.append(f"   in {len(event.active):>2}  round {event.round_no:>2}"
                     f"  {shorten(leader, 22)}")
    return "\n".join(lines)


def shorten(text, width):
    """returns text cut down to width characters"""
    return text if len(text) <= width else text[:width - 1] + "."
