# PracTest1 - reference solution

Reference implementation of Practical Test 1 (Linux
directory structure + `dojo.py` control-structures/validation/random
movement exercise). Intended as a marking/teaching reference, not a
student submission.

## Layout

```
PracTest1/
  activity1_commands.md               Activity 1 - mkdir/tree reference commands (both tree stages)
  control_structures/                 the directory tree built in Activity 1
    if/{if,if_elif,if_elif_else,if_else}/
    loops/for/{for_range,for_each}/, loops/while/
      for_range/dojo.py               <- final dojo.py lives here (Activity 2-4)
  reference_solutions/                dojo.py snapshots, one per activity, for teaching
    dojo_v0_given.py                  the buggy starter code (3 bugs to find)
    dojo_v1_activity2.py              bugs fixed + Step #/spacing
    dojo_v2_activity3.py              + validated num_students/num_steps input
    dojo_v3_activity4_final.py        + randomised move, pos/buffer bounds (== control_structures/.../dojo.py)
```

## Activity 2 bugs (as given)

1. `num_steps == 10` — comparison instead of assignment, should be `=`
2. `for t in range(num_steps)` — missing trailing `:`
3. `print("S S S S S")` — fixed string, doesn't use `pos` for left padding

## Running

```
python dojo.py
```
Requires only the standard library (`random`). On Windows terminals the
🥋 emoji can raise a `UnicodeEncodeError` under the default `cp1252`
console codepage — not a bug in the logic, just a console encoding
issue; run with `PYTHONIOENCODING=utf-8 python dojo.py` or a UTF-8
terminal. The Linux VM used for the real test doesn't hit this.

## Note on `histN.txt`

Activity 1/5 ask for `history > hist1.txt` / `hist2.txt` / `hist3.txt`
from the student's own live terminal session. That can't be
reconstructed after the fact, so it's intentionally not included here —
see `activity1_commands.md` for the commands that would produce it.
