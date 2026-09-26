"""Runs every test in this folder without needing pytest installed.

    python3 tests/run_tests.py            # run everything
    python3 tests/run_tests.py test_events  # run one module

Each test is a module-level function whose name starts with 'test_'.
The same files also run under pytest if it happens to be installed.
"""
import importlib
import os
import sys
import traceback

os.environ.setdefault("MPLBACKEND", "Agg")   # never open a window in tests
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

MODULES = ["test_model", "test_events", "test_competition", "test_scenario",
           "test_reporting", "test_sweep"]


def run_module(name):
    """runs one test module, returning (passed, failures)"""
    module = importlib.import_module(name)
    tests = sorted(item for item in dir(module) if item.startswith("test_"))
    passed, failures = 0, []
    for test_name in tests:
        try:
            getattr(module, test_name)()
            passed += 1
            print(f"  PASS  {name}::{test_name}")
        except Exception:                      # noqa: BLE001 - report anything
            failures.append((f"{name}::{test_name}", traceback.format_exc()))
            print(f"  FAIL  {name}::{test_name}")
    return passed, failures


def main(argv):
    """runs the requested modules and prints a summary"""
    wanted = argv[1:] if len(argv) > 1 else MODULES
    total, all_failures = 0, []
    for name in wanted:
        print(f"{name}:")
        passed, failures = run_module(name)
        total += passed
        all_failures.extend(failures)
    print(f"\n{total} passed, {len(all_failures)} failed")
    for name, detail in all_failures:
        print(f"\n--- {name} ---\n{detail}")
    return 1 if all_failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
