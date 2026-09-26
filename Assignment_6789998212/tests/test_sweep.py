"""Tests for the parameter sweep (the automation bonus)."""
import copy
import os
import tempfile

import helpers
import compSim
import scenario as sc


def sweep_args(**overrides):
    """returns parsed CLI arguments with sweep-friendly defaults"""
    argv = ["--no-animation", "--quiet", "--no-save"]
    for key, value in overrides.items():
        argv.extend([f"--{key.replace('_', '-')}", str(value)])
    return compSim.build_parser().parse_args(argv)


def test_set_in_config():
    """dotted keys reach nested settings and reject unknown ones"""
    config = sc.default_config()
    compSim.set_in_config(config, "competitors.count", "42")
    assert config["competitors"]["count"] == 42
    compSim.set_in_config(config, "max_parallel", "1")
    assert config["max_parallel"] == 1
    try:
        compSim.set_in_config(config, "competitors.height", "3")
        raise AssertionError("unknown key should be rejected")
    except ValueError as problem:
        assert "competitors.height" in str(problem)


def test_sweep_runs():
    """a sweep runs once per value per repeat and tabulates the result"""
    config = sc.default_config(competitors=10, clubs=2, event_count=2,
                               steps=250)
    scenario = sc.Scenario(copy.deepcopy(config), source="unit test")
    printed = []
    args = sweep_args()
    args.sweep = "competitors.count=8,16"
    args.repeats = 2
    args.seed = 1
    rows = compSim.run_sweep(scenario, args, writer=printed.append)
    assert len(rows) == 4
    assert {row["value"] for row in rows} == {"8", "16"}
    assert {row["competitors"] for row in rows} == {8, 16}
    assert all(row["completed"] for row in rows)
    assert all(row["events_held"] >= 1 for row in rows)
    assert any("top club" in line for line in printed)


def test_sweep_writes_csv():
    """the sweep saves its table for the report"""
    scenario = sc.Scenario(sc.default_config(competitors=8, clubs=2,
                                             event_count=2, steps=200),
                           source="unit test")
    with tempfile.TemporaryDirectory() as folder:
        args = sweep_args()
        args.sweep = "seed=1,2"
        args.no_save = False
        args.results_dir = folder
        compSim.run_sweep(scenario, args, writer=lambda *_: None)
        files = os.listdir(folder)
        assert any(name.endswith("_sweep.csv") for name in files), files


def test_main_runs_a_scenario_headless():
    """the whole program runs end to end from the command line"""
    path = os.path.join(helpers.PROJECT, "scenarios", "club_night.json")
    printed = []
    with tempfile.TemporaryDirectory() as folder:
        code = compSim.main(["--scenario", path, "--no-animation", "--quiet",
                             "--results-dir", folder, "--steps", "300"],
                            writer=printed.append)
        assert code == 0
        written = os.listdir(folder)
        assert any(name.endswith("_report.txt") for name in written), written
        assert any(name.endswith("_summary.png") for name in written), written
    assert any("Final standings - clubs" in line for line in printed)


def test_main_reports_a_bad_scenario():
    """a missing scenario file is an explained failure, not a traceback"""
    printed = []
    code = compSim.main(["--scenario", "no_such_file.json", "--no-animation",
                         "--no-save"], writer=printed.append)
    assert code == 2
    assert any("no_such_file.json" in line for line in printed)
