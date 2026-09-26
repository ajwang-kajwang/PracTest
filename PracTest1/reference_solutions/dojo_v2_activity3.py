# Activity 3 - user enters num_students and num_steps, both validated
num_students = int(input("Enter number of students (5-10): "))
while num_students < 5 or num_students > 10:
    print("Out of range, please re-enter...")
    num_students = int(input("Enter number of students (5-10): "))

num_steps = int(input("Enter number of timesteps (10-50): "))
while num_steps < 10 or num_steps > 50:
    print("Out of range, please re-enter...")
    num_steps = int(input("Enter number of timesteps (10-50): "))

pos = 0
for t in range(num_steps):
    print(f"Step {t} :", end="")
    print(" " * pos, end="")
    print("S " * num_students)
    pos += 1
