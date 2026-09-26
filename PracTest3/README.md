# PracTest3 - reference solution

Reference implementation ofPractical Test 3, built against
the **real base code** uploaded after an earlier version of this folder was built purely from
the assignment sheet's images. That earlier version guessed several
interface details wrong - see "Corrections from the pre-basecode
version" below if comparing against anything from before this rebuild.

Intended as a marking/teaching reference, not a student submission.
Characters and setting borrowed from Kung Fu Panda, per the given
`name_defs`.

## Layout

```
characters.py    Student class (given, from basecode/) + two edits students make:
                 - Task 1.d: __str__ now includes position and rank
                 - Task 4.c: step_change(set_move=...) actually applies the
                   given move - the downloaded version's body only ever
                   handled the "random move" branch, despite its own
                   docstring promising otherwise (see below)
training.py      BASE TEMPLATE exactly as downloaded - untouched
task1.py         + 4 more Students, colour-by-rank scatter, savefig('task1.png')
task2.py         + real floor (10 border / 5 centre), Greys/vmin/vmax, user-entered
                 student count with random rank + position kept inside the floor
task3.py         + movement each timestep (step_change()), ax[1] rank bar chart,
                 genuinely single-window animation (see note below)
task4.py         + t==3 centre line-up, t>3 shared random move enforced within
                 the floor's barriers
reference_solutions/
  task3_v1_naive.py   simlength=10 grafted onto task2.py's structure with
                      plt.show() left as-is - opens ten separate blocking
                      windows, confirmed by spying on plt.get_fignums()
                      while it runs. Kept to show why task3.py is built
                      the way it is.
```

## Rank colours

`rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]` (given, in
each task script, not in `characters.py`) - index 0-4 low to high.
Confirmed matplotlib accepts these capitalised strings directly as
`color=` values (it lowercases internally), so no `.lower()` needed
anywhere.

## Two real bugs/gaps found in the given code

1. **`Student.__str__`** only returns `self.name` - Task 1.d exists
   specifically to fix this (see `characters.py`).
2. **`Student.step_change(set_move=...)`** - the given method's
   docstring says it "takes outside movement in set_move", but the
   body only implements the `if not set_move:` (random) branch. Call
   `step_change(set_move=(1, 0))` on the untouched file and *nothing
   happens* - a non-empty tuple is truthy, so the only existing branch
   is skipped and the student's position never updates. Task 4 needs
   `set_move` to actually work (for the synchronised group move), so
   this has to be fixed as part of Task 4, alongside `characters.py`'s
   own docstring already describing the intended behaviour. Confirmed
   empirically before fixing it.

## Why task3.py isn't just "uncomment three lines"

Task 3 step (c) says to add `plt.ion()`, `plt.pause(1)`, `plt.clf()` -
but `training.py`'s loop calls `fig, ax = plt.subplots(2,1,...)` fresh
*inside* the loop. `plt.subplots()` always opens a brand new figure
window; merely uncommenting the other three calls on top of that still
leaves a new window per timestep. Verified this directly: spying on
`plt.get_fignums()` while running `reference_solutions/task3_v1_naive.py`
shows figure numbers `1, 2, 3, ... 10` accumulating one per timestep,
while `task3.py` (which creates `fig = plt.figure()` once, then rebuilds
axes with `fig.subplots(...)` - not `plt.subplots(...)` - after each
`plt.clf()`) stays on figure `1` for all ten timesteps.

## Running

```
python task1.py
python task2.py     # prompts for a student count 1-6
python task3.py      # prompts, then animates 10 timesteps in one window
python task4.py      # prompts, then lines up at t=3 and moves as a group from t=4
```
Requires `numpy` and `matplotlib`.

## Design calls made where the sheet was ambiguous

- **Task 1's five students**: the given `training.py` seeds the list
  with one placeholder Student named `"Shifu"` at `(1,1)`, rank
  `"Black"`. The sheet's own sample output for Task 1 instead shows
  `Panda` first - so `task1.py` replaces the placeholder outright and
  uses `Panda, Tigress, Crane, Viper, Mantis` (the sheet's own sample
  names) rather than literally appending 4 more to the given `Shifu`
  entry. The sheet says names/ranks/positions "are not important", so
  either reading is fine to mark - this one just reproduces the sheet's
  documented sample exactly, which is useful for checking a student's
  own output against it.
- **Floor border thickness**: `BORDER_Y, BORDER_X = 3, 5` on the
  `(20, 40)` given floor shape - not specified exactly on the sheet,
  chosen to visually resemble the sample plots' proportions.
- **`imshow` orientation**: left at the given code's default (no
  `origin=`/`extent=` arguments) rather than adding `origin='lower'`.
  Since neither `imshow` nor `scatter` get an `extent` override, both
  already share the same data-coordinate space, so a student's dot
  lands on the correct floor cell regardless - the only effect of the
  default is that y increases *downward* in the image, which reads
  unusually but isn't a bug worth "fixing" against the given code.
- **Task 1's plot background looks like a solid colour block**: this
  is *expected*, not a mistake - `floor = np.ones((20,40))` is uniform
  at this stage, and Task 2 hints explicitly walk through adding the
  `Greys`/`vmin`/`vmax` control that only makes sense once the array
  has more than one value in it.
- **Task 4 timesteps 0-2**: left un-moved (only the `t==3`/`elif t>3`
  branches exist, no `else`), the direct reading of the sheet's own
  `if`/`elif` pseudocode.
- **A "White" rank is invisible on the Task 3/4 bar chart** (white bar
  on white axes background) - genuinely a property of the given
  `rank_defs` list, not something introduced here; worth flagging to
  students as an observation rather than something to silently "fix".
