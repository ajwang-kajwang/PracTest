"""
wandering3.py - COMP1005 Practical Test 2, Task 3

Sprint 3 goal: move FOUR walkers at once, each taking a random step
each timestep. Positions live in 2D arrays: one row per walker,
one column per timestep (plus the starting column).
"""
import random
import numpy as np
import matplotlib.pyplot as plt

numwalkers = 4
numsteps = 10

x_pos = np.zeros((numwalkers, numsteps + 1), dtype=int)
y_pos = np.zeros((numwalkers, numsteps + 1), dtype=int)

colours = ['red', 'green', 'blue', 'orange']

for step in range(numsteps):                  # outer loop: advance time
    for walker in range(numwalkers):           # inner loop: each walker moves once
        x_move = random.choice([-1, 0, 1])
        y_move = random.choice([-1, 0, 1])
        x_pos[walker, step + 1] = x_pos[walker, step] + x_move
        y_pos[walker, step + 1] = y_pos[walker, step] + y_move

print(x_pos)
print(y_pos)

for walker in range(numwalkers):
    plt.plot(x_pos[walker], y_pos[walker], color=colours[walker],
              marker='o', label=f'walker {walker + 1}')

plt.xlabel('x position')
plt.ylabel('y position')
plt.title('Task 3 - four random walkers')
plt.legend()
plt.show()
