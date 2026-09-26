# Py Kwon Do - Sprint Plan

A path from the PracTest3 code (`Student`, `characters.py`, floor array,
`imshow`/`scatter`, `ion`/`pause`/`clf`) to the `specification.md`.

Each sprint ends with a **checkpoint**: something a student should be
able to show or explain before moving on. Checkpoints double as
practice for the demo.

---

## Running habits (every sprint)

- **Keep incremental versions** (`v1_...`, `v2_...` or git commits).
  The spec's bonus marks depend on discussing extra work in the report,
  and old versions are the evidence.
- **Update the Traceability Matrix as they go**, with feature, code
  reference, test, result and date.
- **Code-quality traps named in the spec:** `while True`, `break`,
  `continue` and global variables all cost marks. Several sprints below
  naturally invite them, and those spots are flagged.

---

## Sprint 0 - Plan on paper (before any code)

**Concept:** design first. The spec explicitly asks for a UML class
diagram and the Traceability Matrix's feature column *before* coding.

- Walk through the 7 assessable features and have students turn each
  into numbered sub-features (1.1, 1.2...) in their matrix.
- Decisions to make and write down:
  - Ranks: which belts, in what order, and whether rank affects performance.
  - Clubs: how many, and where each waits on the floor.
  - Events: at least 2 types, and 4 for full marks. For each, decide
    whether it's individual or group, the rank restrictions, how
    competitors are compared, and what counts as a win.
  - Venue: which areas exist (club areas, event mats, queues).
- UML: which classes exist (Competitor, Event plus subclasses,
  Competition, Venue, maybe Club), what each one *knows*, what each
  one *does*, and how they relate (has-a vs is-a).

**Checkpoint:** a UML diagram and a matrix feature column the student
can talk through without notes.

**Pitfall:** skipping this and designing inside the code. Students who
do usually end up with one huge file and a matrix that doesn't match it.

---

## Sprint 1 - Competitor from Student (Feature 1)

**Concept:** extending an existing class instead of copying it
(inheritance vs. composition), and giving an object *state*.

- Start from PracTest3's `Student`. Ask: should `Competitor` *be* a
  Student (subclass) or *contain* one? Either is defensible, and
  justifying the choice is good report material.
- The spec's attribute list is ID, name, age, club, skills/events, rank,
  position and direction. Map each to a type before writing it.
- Introduce the idea of a competitor **state** (e.g. waiting, going to
  an event, competing, returning). Much of the later logic becomes
  simple once a competitor knows what it's currently doing.
- Generating a varied group of competitors: random vs. from a list/file
  (a seed for Sprint 6's flexibility).

**Pitfall - the `step_change` bug:** the given
`step_change(set_move=...)` silently does nothing when passed a move,
because its body only implements the random branch. Anyone who
inherited `characters.py` unchanged will find their competitors
"refuse to walk to events" in Sprint 3. Don't announce the bug up
front. Ask "does `step_change` do what its docstring says? Prove it."
and let them test it.

**Checkpoint:** create ~10 varied competitors, print them with a useful
`__str__`, and show `step_change` working both with and without
`set_move`.

---

## Sprint 2 - Ranks and the Venue (Features 2 and 5)

**Concept:** representing categories flexibly, and the floor as a map
with meaning.

- Ranks: an ordered list (like `rank_defs`) makes "is this rank high
  enough?" a comparison of positions. Ask how they'd add a new belt
  colour, and whether it takes one change or many.
- Venue: extend the PracTest3 floor array so different values mean
  different areas (club zones, event mats). Keeping each area's
  coordinates in one place (not scattered through the code) pays off
  in Sprints 3 and 4.
- Colour and visibility: rank colour on markers, area colours on the
  floor, and a legend or text labels for which mat is which.

**Pitfall - White rank = 0:** in any "rank number" bar chart, White
belts get a zero-length (invisible) bar, and white markers vanish on
light floors. Prompt them with "Where did your White belts go?" Fixes
are theirs to choose, such as edge colours, a dark floor or shifted
values.

**Pitfall - `imshow` orientation:** the array's row 0 is drawn at the
*top*, so y increases downward. The picture isn't wrong, but students
placing areas "at the top of the floor" often get it upside down.
Checking one known coordinate by eye is a quick test.

**Checkpoint:** plot the empty venue with labelled areas, plus
competitors standing in their club areas, coloured by rank.

---

## Sprint 3 - Moving with purpose (Features 1 and 5)

**Concept:** replacing PracTest3's random walk with *goal-directed*
movement, one step per timestep.

- Give each competitor a target position, and each timestep take one
  step toward it (Moore neighbourhood, like PracTest3), using
  `step_change(set_move=...)` now that it works.
- "Arrived" means position equals target. Discuss what breaks if moves
  can be bigger than one cell or include randomness (they overshoot or
  never match exactly), and whether a tolerance is needed.
- Direction: the spec wants competitors to know which way they face.
  Where does that get updated, and how could it be shown on the plot?
- Barriers: PracTest3 Task 4's "check the move before committing"
  applies here too, keeping everyone on the floor and possibly out of
  other events' mats.
- Animation: reuse PracTest3's single-window approach. Remind them
  that `plt.subplots()` inside the loop opens a new window every
  timestep, and that figure-once plus `fig.subplots()` after `clf()`
  is the fix they already found.

**Pitfall - `while True` / `break`:** "keep stepping until everyone
arrives" is exactly where students reach for these. Steer them toward
the simulation loop they already have, where each timestep *checks* an
arrival condition instead of looping until it's true.

**Checkpoint:** competitors walk from their club areas to a chosen
mat, stop there, and walk back, animated in one window.

---

## Sprint 4 - Events (Feature 3)

**Concept:** a base class with shared behaviour and subclasses that
differ in how they score (polymorphism).

- What every event has: a name, an area, rank eligibility, entrants,
  results, and a way to know if it has started or finished.
- What differs per event type is how it's *run* and scored, which
  makes it the natural method for each subclass to override.
- Lifecycle to design explicitly: eligible competitors are called up,
  queue or walk to the area, the event runs only when all have
  arrived, results are recorded, and competitors return.
- Pairing for sparring: match similar ranks. What happens with an odd
  number of entrants? (A bye, or a three-way bout? Their call.)
- Group or synchronised events: everyone moves together. PracTest3
  Task 4's shared `set_move` plus an all-or-nothing barrier check is
  the direct ancestor.
- Get **two types working end-to-end first**, then add the third and
  fourth. Four half-working types score worse than two solid ones
  during a demo.

**Pitfall - event collisions:** if events start at fixed timesteps, a
competitor eligible for two events gets pulled to the second one
mid-way through the first. Then *neither* event ever sees all its
entrants arrive, and nothing runs. There's no crash; results are just
silently empty. Checkpoint prompt: "What happens to a competitor
who's eligible for two events that overlap?" Students need a rule,
e.g. an event waits until its entrants are free, or entrants are
locked into one event at a time.

**Checkpoint:** two different event types run in sequence with
realistic eligibility, and each produces a ranked or winner result
printed at the end.

---

## Sprint 5 - Competition and Results (Features 4 and 6)

**Concept:** an object that coordinates others, and data worth
reporting.

- Competition owns the schedule: which events run, in what order, and
  whether they can run in parallel on different mats. Parallel events
  make the collision rule from Sprint 4 essential.
- Multi-round formats (heats, then finals) are optional depth. Ask
  whether they're worth the complexity for their design.
- Results by *individual* and by *club* are both required by the spec.
  Where does each score get stored so both views can be built?
- Start with simple statistics (competitors per rank and per club),
  then event placings, then club totals.
- Outputs: printed summaries, plots (the rank bar chart from PracTest3
  is a start) and a saved results file, which is useful evidence for
  the showcase.

**Checkpoint:** one full simulation run from start to finish that
produces a results summary by individual and by club, saved to a file.

---

## Sprint 6 - Flexibility, showcase prep, README (Feature 7)

**Concept:** separating *what* is simulated (parameters) from *how*
(code), so one program produces different scenarios.

- Progression the spec describes: hard-coded values, then prompted
  input with validation, then command-line arguments or config files.
  The validation pattern from PracTest1 (re-prompt while out of range)
  already avoids `while True`, so point students back to it.
- Scenario files (e.g. competitor lists, event schedules) make the
  report's three-scenario showcase reproducible. The spec asks for the
  commands and input files needed to reproduce the results.
- Choose the three showcase scenarios early, so each one shows off
  different features rather than three runs of the same thing.
- Bonus territory (parameter sweeps, better visualisation,
  interactivity) only counts if it's done well *and* discussed in the
  report. Suggest it only once Sprints 1-5 are solid.
- README: file descriptions, dependencies, how to run. Required in the
  zip and easy marks to lose.
- Submission hygiene: the directory must be named `Assignment_<id>`
  with no spaces. The zip needs code, input files, README and report,
  and the report also goes to TurnItIn.

**Checkpoint:** run all three showcase scenarios from the command line
or input files, with no code edits between runs.


## Quick reference: pitfalls by sprint

| Sprint | Pitfall | Symptom students report |
|---|---|---|
| 1, 3 | `step_change(set_move=...)` does nothing (given-code bug) | "My competitors won't walk to the event" |
| 2 | White rank = 0 | "Some bars / markers are missing" |
| 2 | `imshow` row 0 at top | "My area is on the wrong side" |
| 3 | `plt.subplots()` inside the loop | "Dozens of windows pop up" |
| 3 | Exact-match arrival with non-unit moves | "They never arrive / keep jittering" |
| 3, 4 | `while True` / `break` for waiting | Works, but loses code-quality marks |
| 4, 5 | Event collisions (overlapping eligibility) | "The event never starts / results are empty" |
| 4 | Odd number of sparring entrants | "Someone vanishes from the bracket" |
