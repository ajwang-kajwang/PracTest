# Activity 4 (final) - randomised left/right/stay movement, kept on the mat
import random

num_students = int(input("Enter number of students (5-10): "))
while num_students < 5 or num_students > 10:
    print("Out of range, please re-enter...")
    num_students = int(input("Enter number of students (5-10): "))

num_steps = int(input("Enter number of timesteps (10-50): "))
while num_steps < 10 or num_steps > 50:
    print("Out of range, please re-enter...")
    num_steps = int(input("Enter number of timesteps (10-50): "))

space = 3            # padding on each side of the mat before the loop starts
pos = space           # distance of the group from the left edge
buffer = space        # distance of the group from the right edge

for t in range(num_steps):
    move = random.randint(-1, 1)
    new_pos = pos + move
    if 0 <= new_pos <= space * 2:      # only move if it keeps us on the mat
        pos = new_pos
        buffer = space * 2 - pos

    print(f"Step {t:2d} : ", end="")
    print(" " * pos, end="")
    print("\U0001f94b " * num_students, end="")
    print(f": Pos: {pos}, Buffer :{buffer}")
