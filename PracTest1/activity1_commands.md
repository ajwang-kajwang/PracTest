# Activity 1 - Linux command line (reference commands)

Two stages, matching the two tree diagrams on the sheet. Run these for
real in a Linux terminal (or WSL/Git Bash) so `history > histN.txt`
captures what was actually typed - don't fabricate the history files.

## Stage 1 - initial tree

```
mkdir PracTest1
cd PracTest1
mkdir control_structures
cd control_structures
mkdir if for while
tree
cd ~/PracTest1    # or wherever PracTest1 was created
history > hist1.txt
```

Expected `tree` output:

```
control_structures
├── for
├── if
└── while
```

## Stage 2 - expanded tree

`if` becomes a group of four sibling directories (one of them still
called `if`); `for` and `while` move under a new `loops` directory,
and `for` gains two children.

```
cd control_structures
mkdir if/if_elif if/if_elif_else if/if_else
mkdir if/if          # note: nested "if" dir *inside* if/
mkdir loops
mv for while loops/
mkdir loops/for/for_range loops/for/for_each
tree
history > hist2.txt
```

Expected `tree` output:

```
control_structures
├── if
│   ├── if
│   ├── if_elif
│   ├── if_elif_else
│   └── if_else
└── loops
    ├── for
    │   ├── for_each
    │   └── for_range
    └── while
```

`dojo.py` for Activity 2 onward lives in
`control_structures/loops/for/for_range/`.
