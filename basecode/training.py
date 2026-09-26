#
# training.py - training session simulation
#
# Student Name : Ima Student
# Student ID   : 12345678
#
from characters import *
import matplotlib.pyplot as plt
import numpy as np
import random

# rank_defs holds the rank colours and position in list
# indicates level of the rank
rank_defs = ["White", "Yellow", "Green", "Blue", "Black"]
name_defs = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]

floor = np.ones((20,40))

num_steps = 1

students = []
for i in range(1):
    # use the defs lists (above) to build Students
    student = Student("Shifu", (1,1), "Black") 
    students.append(student)

#plt.ion()       # with pause/clf, allows redraw or plots automatically

for t in range(num_steps):
    # make two plots ax[0] and ax[1]
    fig, ax = plt.subplots(2,1, figsize=(10,8))

    # subplot ax[0] 
    ax[0].imshow(floor)  # background colours
    for s in students:
        print(s)
        pos = s.get_pos()
        ax[0].scatter(pos[0], pos[1])

    # subplot ax[1] 
    #name_list = get_namelist(students)
    #rank_cols, rank_nums = get_ranklist(students, rank_defs)
    #print(name_list)
    #print(rank_cols)
    #print(rank_nums)

    #ax[1].barh(name_list)

    #plt.pause(1)
    #plt.clf()
    plt.show()
