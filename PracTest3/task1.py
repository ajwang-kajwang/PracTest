#
# task1.py - COMP1005 Practical Test 3, Task 1
#
# Copied from training.py. Adds four more Students, colours each
# scatter point by rank, and saves the plot. See characters.py for
# the matching __str__() update (Task 1.d).
#
from characters import *
import matplotlib.pyplot as plt
import numpy as np
import random

rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]
name_defs = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]

floor = np.ones((20,40))

num_steps = 1

# Names/ranks/positions aren't marked (sheet: "not important") - using
# the sheet's own sample characters here instead of the given "Shifu"
# placeholder, so this file's output can be checked against it directly.
students = []
students.append(Student("Panda", (10, 11), "Green"))
students.append(Student("Tigress", (11, 13), "Yellow"))
students.append(Student("Crane", (12, 13), "Green"))
students.append(Student("Viper", (14, 13), "Blue"))
students.append(Student("Mantis", (14, 12), "Blue"))

for t in range(num_steps):
    fig, ax = plt.subplots(2,1, figsize=(10,8))

    ax[0].imshow(floor)
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
    fig.savefig('task1.png')
