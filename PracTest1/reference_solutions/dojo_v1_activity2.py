# Activity 2 - bugs fixed, Step # printed with increasing left padding
num_students = 5
num_steps = 10

pos = 0                                  # spaces needed to the left of the group
for t in range(num_steps):
    print(f"Step {t} :", end="")
    print(" " * pos, end="")
    print("S " * num_students)
    pos += 1                             # group drifts one space right each step
