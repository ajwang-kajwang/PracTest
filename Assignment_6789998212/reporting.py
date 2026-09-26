#
# reporting.py - statistics, printed results and saved output
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# Everything that turns a finished (or running) Competition into
# something a human reads: the starting statistics, the per-event
# results, the individual and club standings, a saved text report, a
# results CSV and the summary plots.
#
# Sources / self-citation
# -----------------------
# * The horizontal rank bar chart is the PracTest3 Task 3 ax[1] chart,
#   built with the given get_namelist()/get_ranklist() helpers.
# * Saving a figure with savefig() instead of showing it is the
#   PracTest2 Task 4 approach, which is what makes batch runs possible.
#
import csv
import os


LINE = "=" * 72


def count_by_rank(competitors, ranks):
    """returns how many competitors hold each rank, lowest belt first"""
    return {name: sum(1 for c in competitors if c.get_rank() == name)
            for name in ranks.names()}


def count_by_club(competitors):
    """returns how many competitors each club has, club name order"""
    clubs = sorted({c.get_club() for c in competitors})
    return {club: sum(1 for c in competitors if c.get_club() == club)
            for club in clubs}


def count_by_skill(competitors):
    """returns how many competitors train each kind of event"""
    skills = sorted({skill for c in competitors for skill in c.skills})
    return {skill: sum(1 for c in competitors if skill in c.skills)
            for skill in skills}


def start_lines(competition):
    """returns the 'who turned up' statistics as report lines"""
    competitors = competition.competitors
    lines = [LINE, f"{competition.name} - entry statistics", LINE,
             f"Competitors : {len(competitors)}",
             f"Clubs       : {len(competition.clubs)}",
             f"Venue       : {competition.venue}",
             f"Ranks       : {competition.ranks}", ""]
    lines.append("Competitors at each rank")
    for rank, number in count_by_rank(competitors, competition.ranks).items():
        lines.append(f"    {rank:<8} {'#' * number} {number}")
    lines.append("")
    lines.append("Competitors from each club")
    for club, number in count_by_club(competitors).items():
        lines.append(f"    {club:<18} {'#' * number} {number}")
    lines.append("")
    lines.append("Competitors trained in each event type")
    for skill, number in count_by_skill(competitors).items():
        lines.append(f"    {skill:<14} {'#' * number} {number}")
    return lines


def event_lines(competition):
    """returns every event's result table as report lines"""
    lines = [LINE, "Event results", LINE]
    for event in competition.events:
        lines.extend(event.summary())
        lines.append("")
    return lines


def standings_lines(competition, top=None):
    """returns the individual and club standings as report lines"""
    lines = [LINE, "Final standings - individuals", LINE,
             f"{'Pos':<5}{'Competitor':<16}{'Rank':<8}{'Club':<18}"
             f"{'Pts':>5}  Placings"]
    ordered = competition.standings()
    shown = ordered if top is None else ordered[:top]
    for position, competitor in enumerate(shown, start=1):
        placings = ", ".join(f"{name} {place}{place_suffix(place)}"
                             for name, place, _ in competitor.placings)
        lines.append(f"{position:<5}{competitor.get_name():<16}"
                     f"{competitor.get_rank():<8}{competitor.get_club():<18}"
                     f"{competitor.points:>5}  {placings}")
    lines.extend(["", LINE, "Final standings - clubs", LINE,
                  f"{'Pos':<5}{'Club':<20}{'Pts':>5}{'Golds':>7}{'Size':>6}"])
    clubs = competition.club_standings()
    for position, (club, points, golds) in enumerate(clubs, start=1):
        lines.append(f"{position:<5}{club.name:<20}{points:>5}{golds:>7}"
                     f"{club.size():>6}")
    return lines


def place_suffix(place):
    """returns 'st', 'nd', 'rd' or 'th' for a placing number"""
    if place % 100 in (11, 12, 13):
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(place % 10, "th")


def report_text(competition, scenario_name, source, seed, steps, completed):
    """returns the whole report as one string"""
    header = [LINE,
              f"PY KWON DO SIMULATION REPORT - {scenario_name}",
              LINE,
              f"Scenario source : {source}",
              f"Random seed     : {seed if seed is not None else 'not set'}",
              f"Timestep budget : {steps}",
              f"Timesteps run   : {competition.step_no}",
              f"Finished        : "
              f"{'yes' if completed else 'no - budget spent'}",
              ""]
    parts = (header + start_lines(competition) + [""]
             + event_lines(competition) + standings_lines(competition)
             + ["", LINE, "Commentary", LINE] + competition.log)
    return "\n".join(parts) + "\n"


def write_report(competition, path, scenario_name="scenario",
                 source="built-in", seed=None, steps=0, completed=True):
    """writes the full text report to a file and returns its path"""
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(report_text(competition, scenario_name, source, seed,
                                 steps, completed))
    return path


def write_results_csv(competition, path):
    """writes one row per competitor result, for further analysis"""
    ensure_dir(path)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["competitor_id", "name", "rank", "club", "age",
                         "event", "place", "score", "total_points"])
        for competitor in competition.standings():
            for event_name, place, score in competitor.placings:
                writer.writerow([competitor.comp_id, competitor.get_name(),
                                 competitor.get_rank(), competitor.get_club(),
                                 competitor.get_age(), event_name, place,
                                 score,
                                 competitor.points])
    return path


def ensure_dir(path):
    """creates the folder a file is about to be written into"""
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)


def save_summary_plots(competition, path):
    """saves the four summary charts for a finished competition

    Four panels: competitors per rank, competitors per club, club points
    and the shape of the day (how many people were competing, walking or
    waiting at each timestep).

    Returns
    -------
    str
        the path written
    """
    import matplotlib.pyplot as plt

    ensure_dir(path)
    ranks = competition.ranks
    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(f"{competition.name} - summary", fontsize=14)

    # 1. competitors per rank, drawn in the belt colours.  Edge colours
    # keep the White belt bar visible against the white axes - the
    # PracTest3 "where did my White belts go?" problem.
    counts = count_by_rank(competition.competitors, ranks)
    ax[0, 0].barh(list(counts), list(counts.values()),
                  color=ranks.colours(), edgecolor="black")
    ax[0, 0].set_title("Competitors at each rank")
    ax[0, 0].set_xlabel("competitors")

    # 2. competitors per club
    club_counts = count_by_club(competition.competitors)
    ax[0, 1].bar(list(club_counts), list(club_counts.values()),
                 color="#6699cc", edgecolor="black")
    ax[0, 1].set_title("Competitors from each club")
    ax[0, 1].tick_params(axis="x", rotation=20)

    # 3. final club points
    standings = competition.club_standings()
    ax[1, 0].bar([club.name for club, _, _ in standings],
                 [points for _, points, _ in standings],
                 color="#e0a458", edgecolor="black")
    ax[1, 0].set_title("Club points")
    ax[1, 0].tick_params(axis="x", rotation=20)

    # 4. what everybody was doing, timestep by timestep (NumPy history,
    # in the style of the PracTest2 walker arrays)
    table = competition.history_array()
    if table.size:
        ax[1, 1].plot(table[:, 0], table[:, 1], label="competing")
        ax[1, 1].plot(table[:, 0], table[:, 2], label="walking")
        ax[1, 1].plot(table[:, 0], table[:, 3], label="waiting")
        ax[1, 1].plot(table[:, 0], table[:, 5], label="events finished",
                      linestyle="--")
        ax[1, 1].legend(fontsize=8)
    ax[1, 1].set_title("Shape of the day")
    ax[1, 1].set_xlabel("timestep")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def print_report(competition, scenario_name, source, seed, steps, completed,
                 writer=print):
    """prints the same report that gets written to file"""
    writer(report_text(competition, scenario_name, source, seed, steps,
                       completed))
