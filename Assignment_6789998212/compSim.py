#
# compSim.py - run a Py Kwon Do competition simulation
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# This is the program you run.  Everything it needs to know about WHAT
# to simulate comes from the command line, a scenario file or - if you
# give it nothing - a few validated questions, so the same code
# produces completely different competitions without being edited.
#
# Examples
# --------
#   python3 compSim.py
#   python3 compSim.py --scenario scenarios/club_night.json
#   python3 compSim.py --scenario scenarios/regional_titles.json --seed 5
#   python3 compSim.py --scenario scenarios/national_grading.json \
#           --no-animation
#   python3 compSim.py --scenario scenarios/regional_titles.json \
#           --sweep competitors.count=12,24,36 --repeats 3
#
# Sources / self-citation
# -----------------------
# * The timestep printout is the PracTest3 Task 3/4 "#### TIMESTEP n ####"
#   listing, trimmed to the competitors who are actually doing something.
# * Falling back to prompted, validated input follows PracTest1's
#   dojo.py (see scenario.ask_int).
#
import argparse
import glob
import os
import sys

import scenario as sc

HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIO_DIR = os.path.join(HERE, "scenarios")
RESULTS_DIR = os.path.join(HERE, "results")


def build_parser():
    """returns the command line parser

    Every simulation parameter that is worth varying between runs has a
    switch here, so the three showcase runs in the report need no code
    edits at all.
    """
    parser = argparse.ArgumentParser(
        prog="compSim.py",
        description="Simulate a Py Kwon Do martial arts competition.",
        epilog="With no --scenario the program asks for the numbers it needs.")
    parser.add_argument("--scenario", metavar="FILE",
                        help="JSON scenario file to run")
    parser.add_argument("--list-scenarios", action="store_true",
                        help="list the scenario files that ship with "
                             "the program")
    parser.add_argument("--seed", type=int, metavar="N",
                        help="random seed, overriding the scenario's own")
    parser.add_argument("--steps", type=int, metavar="N",
                        help="timestep budget, overriding the scenario's own")
    parser.add_argument("--speed", type=float, default=0.35, metavar="SECONDS",
                        help="pause between animation frames (default 0.35)")
    parser.add_argument("--no-animation", action="store_true",
                        help="run without the live plot (for batch runs)")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the final report, not every timestep")
    parser.add_argument("--results-dir", default=RESULTS_DIR, metavar="DIR",
                        help="where the report, CSV and plots are written")
    parser.add_argument("--no-save", action="store_true",
                        help="do not write any output files")
    parser.add_argument("--sweep", metavar="KEY=V1,V2,...",
                        help="run one simulation per value of a scenario "
                             "setting, e.g. competitors.count=12,24,36")
    parser.add_argument("--repeats", type=int, default=1, metavar="N",
                        help="seeds per sweep value (default 1)")
    return parser


# --- helpers ------------------------------------------------------------
def slug(text):
    """returns a filename-safe version of a scenario name"""
    keep = [char.lower() if char.isalnum() else "_" for char in text]
    return "".join(keep).strip("_")


def list_scenarios(writer=print):
    """prints the scenario files that ship with the program"""
    paths = sorted(glob.glob(os.path.join(SCENARIO_DIR, "*.json")))
    if not paths:
        writer(f"No scenario files found in {SCENARIO_DIR}")
        return paths
    writer("Available scenarios:")
    for path in paths:
        try:
            name = sc.Scenario.load(path).name()
        except ValueError as problem:
            name = f"(unreadable: {problem})"
        writer(f"    {os.path.relpath(path, HERE):<40} {name}")
    return paths


def choose_scenario(args, reader=input, writer=print):
    """returns the Scenario to run, from a file or from prompts"""
    if args.scenario:
        return sc.Scenario.load(args.scenario)
    return sc.Scenario.from_prompt(reader=reader, writer=writer)


def make_reporter(competition, quiet, writer=print):
    """returns the per-timestep callback used while the sim runs

    Prints only what changed: any new commentary, plus a one-line
    headcount, which keeps a 200-timestep run readable.
    """
    seen = {"lines": 0}

    def report(comp):
        """prints this timestep's news"""
        fresh = comp.log[seen["lines"]:]
        seen["lines"] = len(comp.log)
        for line in fresh:
            writer(line)
        if not quiet:
            snapshot = comp.history[-1]
            writer(f"[t={comp.step_no:3d}] "
                   f"competing {snapshot['competing']:>2}"
                   f" | walking {snapshot['walking']:>2}"
                   f" | waiting {snapshot['waiting']:>2}"
                   f" | events running {snapshot['events_live']}"
                   f" done {snapshot['events_done']}")

    return report


def save_outputs(competition, scenario, args, seed, steps, completed,
                 view=None, writer=print):
    """writes the report, the results CSV and the summary plots"""
    import reporting

    if args.no_save:
        return {}
    folder = args.results_dir
    stem = os.path.join(folder, slug(scenario.name()))
    final_frame = view
    if final_frame is None:
        # A headless run still gets one picture of the venue at the end,
        # which is the evidence the report needs for a batch run.
        import visualise
        final_frame = visualise.SimView(competition, interactive=False)
        final_frame.update(competition)
    written = {
        "report": reporting.write_report(
            competition, f"{stem}_report.txt", scenario.name(),
            scenario.source, seed, steps, completed),
        "csv": reporting.write_results_csv(competition, f"{stem}_results.csv"),
        "summary": reporting.save_summary_plots(
            competition, f"{stem}_summary.png"),
    }
    written["final_frame"] = final_frame.save(f"{stem}_final.png")
    if view is None:
        final_frame.close()
    for kind, path in written.items():
        writer(f"Saved {kind:<12} -> {os.path.relpath(path, HERE)}")
    return written


# --- a single run --------------------------------------------------------
def run_once(scenario, args, writer=print):
    """runs one simulation and returns (competition, completed, seed)

    Returns
    -------
    tuple
        the finished Competition, whether it completed inside its
        timestep budget, and the seed that was used
    """
    competition, steps = scenario.build(seed=args.seed, steps=args.steps)
    seed = scenario.seed(args.seed)
    view = None
    if not args.no_animation:
        import visualise
        view = visualise.SimView(competition, pause=args.speed)
    writer(f"Running {scenario} for up to {steps} timesteps "
           f"(seed {seed if seed is not None else 'not set'})")
    completed = competition.run(steps, view=view,
                                on_step=make_reporter(competition, args.quiet,
                                                      writer))
    if not completed:
        writer(f"Timestep budget of {steps} spent before the competition "
               f"finished - try a larger --steps.")
    return competition, completed, seed, steps, view


# --- parameter sweep (bonus) --------------------------------------------
def set_in_config(config, dotted_key, value):
    """sets config['a']['b'] from the key 'a.b', converting the value

    Numbers are stored as numbers so the scenario validator sees what
    it expects; anything else is left as text.
    """
    parts = dotted_key.split(".")
    target = config
    for part in parts[:-1]:
        if part not in target or not isinstance(target[part], dict):
            raise ValueError(f"--sweep key {dotted_key!r} is not part of "
                             f"this scenario")
        target = target[part]
    if parts[-1] not in target and parts[-1] not in ("seed", "steps"):
        raise ValueError(f"--sweep key {dotted_key!r} is not part of "
                         f"this scenario")
    number = sc.parse_int(value)
    target[parts[-1]] = value if number is None else number
    return config


def run_sweep(scenario, args, writer=print):
    """runs the scenario once per swept value and tabulates the results

    This is the "parameter sweep" bonus: the same scenario, one setting
    varied, every run headless and seeded so the comparison is fair and
    reproducible.

    Returns
    -------
    list
        one result dict per run
    """
    import copy

    import reporting

    key, _, values = args.sweep.partition("=")
    if not values:
        raise ValueError("--sweep needs KEY=VALUE1,VALUE2,... "
                         "e.g. competitors.count=12,24,36")
    rows = []
    for value in values.split(","):
        for repeat in range(max(1, args.repeats)):
            config = set_in_config(copy.deepcopy(scenario.config), key.strip(),
                                   value.strip())
            variant = sc.Scenario(
                config, source=f"{scenario.source} [{key}={value}]")
            seed = (args.seed if args.seed is not None else 0) + repeat
            competition, steps = variant.build(seed=seed, steps=args.steps)
            completed = competition.run(steps)
            leaders = competition.club_standings()
            rows.append({
                "value": value.strip(),
                "seed": seed,
                "steps": competition.step_no,
                "completed": completed,
                "competitors": len(competition.competitors),
                "events_held": len(competition.held_events()),
                "top_club": leaders[0][0].name if leaders else "-",
                "top_points": leaders[0][1] if leaders else 0,
            })
            writer(f"  {key}={value.strip():<6} seed {seed} -> "
                   f"{competition.step_no:>4} timesteps, "
                   f"{len(competition.held_events())} events held, "
                   f"winner {rows[-1]['top_club']}")
    writer("")
    writer(f"{'value':<10}{'seed':>6}{'steps':>8}{'held':>6}{'finished':>10}"
           f"  top club")
    for row in rows:
        writer(f"{row['value']:<10}{row['seed']:>6}{row['steps']:>8}"
               f"{row['events_held']:>6}{str(row['completed']):>10}"
               f"  {row['top_club']} ({row['top_points']} pts)")
    if not args.no_save:
        import csv
        path = os.path.join(args.results_dir,
                            f"{slug(scenario.name())}_sweep.csv")
        reporting.ensure_dir(path)
        with open(path, "w", newline="", encoding="utf-8") as handle:
            output = csv.DictWriter(handle, fieldnames=list(rows[0]))
            output.writeheader()
            output.writerows(rows)
        writer(f"Saved sweep       -> {os.path.relpath(path, HERE)}")
    return rows


# --- entry point ---------------------------------------------------------
def main(argv=None, writer=print):
    """parses the command line and runs whatever was asked for

    Returns
    -------
    int
        process exit code: 0 for success, 2 for a bad scenario
    """
    args = build_parser().parse_args(argv)
    if args.list_scenarios:
        list_scenarios(writer)
        return 0
    try:
        scenario = choose_scenario(args, writer=writer)
        if args.sweep:
            args.no_animation = True
            run_sweep(scenario, args, writer)
            return 0
        competition, completed, seed, steps, view = run_once(
            scenario, args, writer)
    except ValueError as problem:
        writer(f"Could not run that scenario: {problem}")
        return 2

    import reporting
    reporting.print_report(competition, scenario.name(), scenario.source,
                           seed, steps, completed, writer)
    save_outputs(competition, scenario, args, seed, steps, completed, view,
                 writer)
    if view is not None:
        writer("Close the plot window to finish.")
        import matplotlib.pyplot as plt
        plt.ioff()
        plt.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
