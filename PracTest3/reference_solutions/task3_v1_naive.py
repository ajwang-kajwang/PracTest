#
# task3_v1_naive.py
#
# Intermediate/teaching-only version: simlength changed to 10 and the
# timestep added to the suptitle, but plt.subplots()/plt.show() are
# still called fresh every timestep (as in task2.py), so this pops up
# TEN separate blocking windows - exactly what step (b) describes.
# Kept only to show why step (c) is needed; the real deliverable is
# task3.py, not this file.
#
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import *
import matplotlib.pyplot as plt
import numpy as np
import random

rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]
name_defs = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]

floor = np.full((20, 40), 10)
BORDER_Y, BORDER_X = 3, 5
floor[BORDER_Y:-BORDER_Y, BORDER_X:-BORDER_X] = 5

simlength = 10

num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))
while num_students < 1 or num_students > len(name_defs):
    print('Out of range, please re-enter...')
    num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))

students = []
for i in range(num_students):
    rank = random.choice(rank_defs)
    x = random.randint(BORDER_X, 40 - BORDER_X - 1)
    y = random.randint(BORDER_Y, 20 - BORDER_Y - 1)
    students.append(Student(name_defs[i], (x, y), rank))

for t in range(simlength):
    for s in students:
        s.step_change()

    fig, ax = plt.subplots(2,1, figsize=(10,8))    # <- a brand new figure every time

    ax[0].imshow(floor, cmap='Greys', vmin=0, vmax=10)
    x_values = [s.get_pos()[0] for s in students]
    y_values = [s.get_pos()[1] for s in students]
    colours = [s.get_rank() for s in students]
    ax[0].scatter(x_values, y_values, marker='o', color=colours)
    ax[0].set_title('Class Map')

    name_list = get_namelist(students)
    rank_cols, rank_nums = get_ranklist(students, rank_defs)
    ax[1].barh(name_list, rank_nums, color=rank_cols)
    ax[1].set_title('Student Rankings')

    fig.suptitle(f"Master Shifu's School - Timestep # {t}")

    print(f'#### TIMESTEP {t} ####')
    for s in students:
        print(s)

    plt.show()      # blocks until closed, and leaves a new window behind each time
