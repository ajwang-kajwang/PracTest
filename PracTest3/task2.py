#
# task2.py - COMP1005 Practical Test 3, Task 2
#
# Copied from task1.py. The floor array now has real structure (10 =
# black border, 5 = dark grey centre), rendered with the "Greys"
# colormap and explicit vmin/vmax. The user is asked how many students
# to place, each given a random rank and a random position that stays
# within the floor's grey interior.
#
from characters import *
import matplotlib.pyplot as plt
import numpy as np
import random

rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]
name_defs = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]

floor = np.full((20, 40), 10)     # black border
BORDER_Y, BORDER_X = 3, 5          # thickness of the border on each side
floor[BORDER_Y:-BORDER_Y, BORDER_X:-BORDER_X] = 5   # dark grey centre

num_steps = 1

num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))
while num_students < 1 or num_students > len(name_defs):
    print('Out of range, please re-enter...')
    num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))

students = []
for i in range(num_students):
    rank = random.choice(rank_defs)
    # keep everyone in the grey interior, off the black border
    x = random.randint(BORDER_X, 40 - BORDER_X - 1)
    y = random.randint(BORDER_Y, 20 - BORDER_Y - 1)
    students.append(Student(name_defs[i], (x, y), rank))

for t in range(num_steps):
    fig, ax = plt.subplots(2,1, figsize=(10,8))

    ax[0].imshow(floor, cmap='Greys', vmin=0, vmax=10)
    x_values = [s.get_pos()[0] for s in students]
    y_values = [s.get_pos()[1] for s in students]
    colours = [s.get_rank() for s in students]
    ax[0].scatter(x_values, y_values, marker='o', color=colours)
    ax[0].set_title('Class Map')

    for s in students:
        print(s)

    name_list = get_namelist(students)
    rank_cols, rank_nums = get_ranklist(students, rank_defs)
    print(name_list)
    print(rank_nums)

    fig.suptitle("Master Shifu's School")
    fig.savefig('task2.png')
