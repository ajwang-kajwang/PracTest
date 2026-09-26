# Py Kwon Do - Traceability Matrix

Student Name : ajwang-kajwang
Student ID   : 6789998212

The Feature column was written in Sprint 0, before any code, and then
used as the build checklist. Code / Test / Result / Date columns were
filled in as each sub-feature was finished.

Status key: DONE = implemented and tested, PART = partially done.

## 1. Competitors

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 1.1 | Competitor is an object extending the given `Student` | `pykwondo.py` `Competitor` | `tests/test_model.py::test_competitor_extends_student` | DONE | 2026-09-26 |
| 1.2 | Knows ID, name, age, club, skills, rank, position, direction | `pykwondo.py` `Competitor.__init__` | `tests/test_model.py::test_competitor_attributes` | DONE | 2026-09-26 |
| 1.3 | Useful `__str__` for printing each timestep | `pykwondo.py` `Competitor.__str__` | `tests/test_model.py::test_competitor_str` | DONE | 2026-09-26 |
| 1.4 | Movement implemented in `step_change()`, one cell per timestep | `pykwondo.py` `Competitor.step_change` | `tests/test_model.py::test_step_change_targets` | DONE | 2026-09-26 |
| 1.5 | `step_change(set_move=...)` honours an externally supplied move (given-code bug fixed) | `characters.py` `Student.step_change`, `pykwondo.py` `Competitor.step_change` | `tests/test_model.py::test_step_change_set_move` | DONE | 2026-09-26 |
| 1.6 | Competitor state machine (waiting / travelling / ready / competing / returning) | `pykwondo.py` `Competitor` state constants | `tests/test_model.py::test_state_transitions` | DONE | 2026-09-26 |
| 1.7 | Waits in its club area, moves to the event queue when its event starts, returns after | `competition.py` `Competition.step` | `tests/test_competition.py::test_full_run_returns_home` | DONE | 2026-09-26 |
| 1.8 | Direction is tracked and updated as they move / perform | `pykwondo.py` `Competitor._face` | `tests/test_model.py::test_direction_updates` | DONE | 2026-09-26 |
| 1.9 | Competitors vary (age, form, skills, rank, club) | `scenario.py` `build_competitors` | `tests/test_scenario.py::test_generated_roster_varies` | DONE | 2026-09-26 |

## 2. Levels / Ranks

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 2.1 | Ordered rank list extending the given `rank_defs` | `pykwondo.py` `RankSystem`, `DEFAULT_RANKS` | `tests/test_model.py::test_rank_order` | DONE | 2026-09-26 |
| 2.2 | Rank has a colour, used when plotting competitors | `visualise.py` `SimView.draw_venue` | evidence: `results/*_final.png` | DONE | 2026-09-26 |
| 2.3 | Rank qualifies / disqualifies for events | `events.py` `Event.is_eligible` | `tests/test_events.py::test_eligibility_rank_band` | DONE | 2026-09-26 |
| 2.4 | Rank affects performance (higher belt = higher base skill) | `pykwondo.py` `Competitor.performance` | `tests/test_model.py::test_rank_affects_performance` | DONE | 2026-09-26 |
| 2.5 | Ranks are extensible from a scenario file without code changes | `scenarios/*.json` `ranks` block | `tests/test_scenario.py::test_custom_ranks` | DONE | 2026-09-26 |
| 2.6 | White belts stay visible on plots and bar charts | `visualise.py` edge colours + rank level, `reporting.py` bar charts | evidence: `results/*_summary.png` (White bar has an edge and a length) | DONE | 2026-09-26 |

## 3. Events / Activities

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 3.1 | Event base class with shared lifecycle | `events.py` `Event` | `tests/test_events.py::test_lifecycle_states`, `::test_make_event_from_config` | DONE | 2026-09-26 |
| 3.2 | Type 1 - individual pattern (sequence of moves, direction + action) | `events.py` `PatternEvent` | `tests/test_events.py::test_pattern_event_ranks_entrants` | DONE | 2026-09-26 |
| 3.3 | Type 2 - sparring, paired by similar rank, single elimination | `events.py` `SparringEvent` | `tests/test_events.py::test_sparring_pairs_by_rank` | DONE | 2026-09-26 |
| 3.4 | Type 3 - group / synchronised team pattern (moves together) | `events.py` `TeamPatternEvent` | `tests/test_events.py::test_team_event_moves_together` | DONE | 2026-09-26 |
| 3.5 | Type 4 - specialist technique (board breaking, escalating rounds) | `events.py` `BreakingEvent` | `tests/test_events.py::test_breaking_event_eliminates` | DONE | 2026-09-26 |
| 3.6 | Competitors move to the event area and the event only starts when all have arrived | `events.py` `Event.call_up`, `everyone_arrived` | `tests/test_events.py::test_waits_for_arrivals` | DONE | 2026-09-26 |
| 3.7 | Odd number of sparring entrants handled by a bye | `events.py` `SparringEvent._pair_up` | `tests/test_events.py::test_sparring_bye_for_odd` | DONE | 2026-09-26 |
| 3.8 | Events produce a ranked result / winner | `events.py` `Event.placings` | `tests/test_events.py::test_every_event_produces_placings` | DONE | 2026-09-26 |

## 4. Competition

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 4.1 | Competition owns a series of events and steps the simulation | `competition.py` `Competition.step` | `tests/test_competition.py::test_full_run_completes` | DONE | 2026-09-26 |
| 4.2 | Events may run in parallel on different mats | `competition.py` `Competition._activate_events` | `tests/test_competition.py::test_parallel_events_on_free_mats` | DONE | 2026-09-26 |
| 4.3 | A competitor is locked to one event at a time (no overlap deadlock) | `competition.py` `Competition._activate_events`, `pykwondo.py` `Competitor.is_free` | `tests/test_competition.py::test_overlapping_eligibility_no_deadlock` | DONE | 2026-09-26 |
| 4.4 | Eligible competitors are included automatically | `events.py` `Event.call_up` | `tests/test_competition.py::test_eligible_are_called_up` | DONE | 2026-09-26 |
| 4.5 | Performance tracked per individual and per club | `competition.py` `Competition.award` | `tests/test_competition.py::test_points_awarded` | DONE | 2026-09-26 |
| 4.6 | Simulation terminates when every event is finished and everyone is home | `competition.py` `Competition.is_complete` | `tests/test_competition.py::test_full_run_completes` | DONE | 2026-09-26 |
| 4.7 | An event nobody can enter is abandoned instead of blocking the schedule | `competition.py` `Competition.abandon_impossible_events` | `tests/test_competition.py::test_impossible_event_is_abandoned` | DONE | 2026-09-26 |

## 5. Venue

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 5.1 | Floor map as a coded grid array (extends PracTest3's floor) | `pykwondo.py` `Venue.grid` | `tests/test_model.py::test_venue_grid_codes` | DONE | 2026-09-26 |
| 5.2 | Club areas and event mats are colour-coded and labelled | `visualise.py` `SimView.draw_venue`, `pykwondo.py` `Venue.colour_table` | evidence: `results/*_final.png` | DONE | 2026-09-26 |
| 5.3 | Competitors drawn on the map coloured by rank | `visualise.py` `SimView.draw_venue` | evidence: `results/*_final.png` | DONE | 2026-09-26 |
| 5.4 | Facing direction shown on the map | `visualise.py` quiver arrows | `tests/test_model.py::test_direction_updates`, evidence: `results/*_final.png` | DONE | 2026-09-26 |
| 5.5 | State shown on the map (marker shape per state) | `visualise.py` `STATE_MARKERS` | `tests/test_reporting.py::test_state_markers_cover_every_state` | DONE | 2026-09-26 |
| 5.6 | Walls / barriers - nobody walks off the floor | `pykwondo.py` `Venue.is_walkable` | `tests/test_model.py::test_barrier_blocks_move` | DONE | 2026-09-26 |
| 5.7 | Venue layout is generated from the scenario (clubs and mats counted, not hard-coded) | `pykwondo.py` `Venue.build_default` | `tests/test_scenario.py::test_venue_scales_with_clubs` | DONE | 2026-09-26 |
| 5.8 | Single animation window (PracTest3 `ion`/`pause`/`clf` fix) | `visualise.py` `SimView` | `tests/test_reporting.py::test_live_view_uses_one_window` (asserts one figure after 12 redraws) | DONE | 2026-09-26 |

## 6. Results

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 6.1 | Starting statistics - competitors per rank and per club | `reporting.py` `count_by_rank`, `count_by_club` | `tests/test_reporting.py::test_counts` | DONE | 2026-09-26 |
| 6.2 | Per-event results (placings / winners) printed and saved | `reporting.py` `write_report` | `tests/test_reporting.py::test_report_contains_events` | DONE | 2026-09-26 |
| 6.3 | Individual standings across the whole competition | `competition.py` `Competition.standings` | `tests/test_competition.py::test_points_awarded` | DONE | 2026-09-26 |
| 6.4 | Club standings across the whole competition | `competition.py` `Competition.club_standings` | `tests/test_competition.py::test_points_awarded` | DONE | 2026-09-26 |
| 6.5 | Progressive (live) results during the run | `visualise.py` `draw_club_points`, `status_text` | `tests/test_reporting.py::test_status_text_lists_every_event` | DONE | 2026-09-26 |
| 6.6 | Report saved to a file | `reporting.py` `write_report` | `tests/test_reporting.py::test_report_written` | DONE | 2026-09-26 |
| 6.7 | Summary plots saved to a file | `reporting.py` `save_summary_plots` | `tests/test_reporting.py::test_report_written` | DONE | 2026-09-26 |

## 7. Flexibility and usability

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| 7.1 | Prompted input with validation (no `while True`) | `scenario.py` `ask_int`, `Scenario.from_prompt` | `tests/test_scenario.py::test_ask_int_revalidates`, `::test_prompted_scenario_builds` | DONE | 2026-09-26 |
| 7.2 | Command line arguments control the run | `compSim.py` `build_parser`, `main` | `tests/test_scenario.py::test_cli_parses`, `tests/test_sweep.py::test_main_runs_a_scenario_headless` | DONE | 2026-09-26 |
| 7.3 | Scenario configuration files (JSON) | `scenario.py` `Scenario.load` | `tests/test_scenario.py::test_load_each_scenario` | DONE | 2026-09-26 |
| 7.4 | Competitor roster from a CSV input file | `scenario.py` `load_roster` | `tests/test_scenario.py::test_roster_csv` | DONE | 2026-09-26 |
| 7.5 | Reproducible runs via `--seed` | `compSim.py`, `competition.py` rng | `tests/test_scenario.py::test_seed_reproducible` | DONE | 2026-09-26 |
| 7.6 | Three showcase scenarios runnable with no code edits | `scenarios/*.json`, `run_showcase.sh` | `tests/test_scenario.py::test_load_each_scenario`, evidence: `results/` | DONE | 2026-09-26 |
| 7.7 | Scenario files validated with clear error messages | `scenario.py` `validate_config` | `tests/test_scenario.py::test_bad_config_message`, `tests/test_sweep.py::test_main_reports_a_bad_scenario` | DONE | 2026-09-26 |
| 7.8 | Headless operation for automated / batch runs | `compSim.py` `--no-animation` | `tests/test_scenario.py::test_cli_parses` | DONE | 2026-09-26 |

## Bonus / extra work

| # | Feature | Code | Test | Result | Date |
|---|---|---|---|---|---|
| B.1 | Parameter sweep across a scenario, results tabulated | `compSim.py` `run_sweep`, `set_in_config` | `tests/test_sweep.py::test_sweep_runs`, `::test_sweep_writes_csv`, `::test_set_in_config`, evidence: `results/regional_titles_sweep.csv` | DONE | 2026-09-26 |
| B.2 | Live dashboard (venue + rank chart + club points + event status) | `visualise.py` `SimView.update` | `tests/test_reporting.py::test_live_view_uses_one_window`, evidence: `results/*_final.png` | DONE | 2026-09-26 |
| B.3 | Per-timestep history recorded for after-the-fact analysis | `competition.py` `Competition.history` | `tests/test_competition.py::test_history_recorded` | DONE | 2026-09-26 |

## Notes kept while building

* **Sprint 4 collision, found by running it.** The first version of
  `Competition.events_to_start()` checked each pending event on its own,
  so two events whose eligible pools overlapped were both started on
  the same timestep; the second called up an empty entry list and was
  never held.  In `national_grading.json` that silently dropped two of
  the six events (the commentary showed `called up 0 competitors`).
  Fixed by tracking the competitors that the events chosen this
  timestep are about to claim.
* **`--speed 0` hung the animation.** `plt.pause(0)` runs the backend
  event loop with no timeout.  The pause is now clamped to
  `MIN_PAUSE = 0.001` in `visualise.py`.
* **Events that cannot be filled right now versus ever.** `call_up()`
  originally marked an event "not held" when too few competitors were
  free, which killed events that were only temporarily short.  Now
  `call_up()` simply returns and the event stays pending; only
  `abandon_impossible_events()`, which looks at the whole roster, gives
  up on one permanently.
