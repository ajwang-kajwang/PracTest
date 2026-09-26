# PracTest2 - reference solution

Reference implementation of Practical Test 2 (random walk /
"wandering" exercise), built up task-by-task exactly as the test sheet
specifies. Intended as a marking/teaching reference, not a student
submission.

## Files

| File | Task | What it adds over the previous file |
|---|---|---|
| `wandering1.py` | 1 | Single walker, plain Python lists, red line + triangles |
| `wandering2.py` | 2 | Same walk, NumPy integer arrays, side-by-side subplot vs. Task 1 |
| `wandering3.py` | 3 | Four walkers, 2D arrays (`numwalkers x numsteps+1`), random `[-1,0,1]` moves each step |
| `wandering4.py` | 4 | User picks 1-4 walkers to plot, 2x2 grid, validated input, saved to `wandering4.png` |

## Running

```
python wandering1.py
python wandering2.py
python wandering3.py
python wandering4.py    # prompts for a number 1-4, writes wandering4.png
```

Requires `numpy` and `matplotlib` (`pip3 install numpy matplotlib`).

## Note on `hist.txt`

The test sheet asks students to run `history > hist.txt` in their own
terminal to record the commands they actually typed while working.
That only means something inside a real, live session - it can't be
reconstructed after the fact, so it's intentionally not included here.
