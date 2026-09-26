"""
wandering4.py - COMP1005 Practical Test 2, Task 4

Sprint 4 goal: same four walkers as Task 3, but the user picks how
many (1-4) get plotted, laid out left-to-right/top-to-bottom in a
2x2 grid. Unused subplots are left blank. Output is saved to a file
instead of shown on screen.
"""
import random
import numpy as np
import matplotlib.pyplot as plt

numwalkers = 4
numsteps = 10

# --- validate the user's answer before doing anything else --------------
while True:
    try:
        num_to_plot = int(input('How many walkers do you want to plot (1-4)? '))
        if 1 <= num_to_plot <= 4:
            break
        print('Please enter a whole number between 1 and 4.')
    except ValueError:
        print('Please enter a whole number between 1 and 4.')

x_pos = np.zeros((numwalkers, numsteps + 1), dtype=int)
y_pos = np.zeros((numwalkers, numsteps + 1), dtype=int)
colours = ['red', 'green', 'blue', 'orange']

for step in range(numsteps):
    for walker in range(numwalkers):
        x_pos[walker, step + 1] = x_pos[walker, step] + random.choice([-1, 0, 1])
        y_pos[walker, step + 1] = y_pos[walker, step] + random.choice([-1, 0, 1])

fig, axes = plt.subplots(2, 2)
fig.suptitle('Task 4 - user-chosen number of walkers')

for walker in range(numwalkers):
    row, col = divmod(walker, 2)               # 0,1 -> row 0 ; 2,3 -> row 1
    ax = axes[row, col]
    if walker < num_to_plot:
        ax.plot(x_pos[walker], y_pos[walker], color=colours[walker], marker='o')
        ax.set_title(f'walker {walker + 1}')
    # else: walker not requested -> subplot stays blank

plt.savefig('wandering4.png')
print('Saved plot to wandering4.png')
