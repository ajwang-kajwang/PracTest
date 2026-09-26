#
# task4.py - COMP1005 Practical Test 3, Task 4
#
# Copied from task3.py. At t == 3 the students line up together in the
# centre of the floor; from then on they all take the SAME random step
# each timestep, but only if that step keeps every one of them on the
# floor (the "barrier") - otherwise nobody moves that timestep. Needs
# the Task 4.c fix to Student.step_change() in characters.py, which
# the given file never actually implemented for set_move.
#
from characters import *
import matplotlib.pyplot as plt
import numpy as np
import random

rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]
name_defs = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]

floor = np.full((20, 40), 10)
BORDER_Y, BORDER_X = 3, 5
floor[BORDER_Y:-BORDER_Y, BORDER_X:-BORDER_X] = 5

# interior bounds - one cell in from the black border wall on every side
MIN_X, MAX_X = BORDER_X, 40 - BORDER_X - 1
MIN_Y, MAX_Y = BORDER_Y, 20 - BORDER_Y - 1

simlength = 10
centre_x = 40 // 2
centre_y = 20 // 2

num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))
while num_students < 1 or num_students > len(name_defs):
    print('Out of range, please re-enter...')
    num_students = int(input(f'Enter number of students (1-{len(name_defs)}): '))

students = []
for i in range(num_students):
    rank = random.choice(rank_defs)
    x = random.randint(MIN_X, MAX_X)
    y = random.randint(MIN_Y, MAX_Y)
    students.append(Student(name_defs[i], (x, y), rank))

plt.ion()
fig = plt.figure(figsize=(10, 8))

for t in range(simlength):
    if t == 3:
        # line everyone up, evenly spaced, across the centre of the floor
        start_x = centre_x - (num_students - 1)
        for i, s in enumerate(students):
            s.set_pos((start_x + 2 * i, centre_y))
    elif t > 3:
        move_x = random.randint(-1, 1)
        move_y = random.randint(-1, 1)
        move_is_safe = all(
            MIN_X <= s.get_pos()[0] + move_x <= MAX_X
            and MIN_Y <= s.get_pos()[1] + move_y <= MAX_Y
            for s in students
        )
        if move_is_safe:
            for s in students:
                s.step_change(set_move=(move_x, move_y))
        # else: the move would put someone into the wall - nobody moves

    plt.clf()
    ax = fig.subplots(2,1)

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
    fig.tight_layout(rect=[0, 0, 1, 0.94])

    print(f'#### TIMESTEP {t} ####')
    for s in students:
        print(s)

    plt.pause(1)
