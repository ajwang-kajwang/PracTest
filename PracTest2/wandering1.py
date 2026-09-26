"""
wandering1.py - COMP1005 Practical Test 2, Task 1

Sprint 1 goal: build a random walk out of plain Python LISTS.

The walker starts at (0, 0). x_moves/y_moves hold the STEP taken at
each moment (-1, 0 or +1). x_pos/y_pos hold the walker's cumulative
POSITION after each step - that's the thing we actually plot.
"""
import matplotlib.pyplot as plt

# Starter data (on the real test this comes from the wandering.py
# template downloaded from Blackboard) - one step per list element.
x_moves = [1, 0, 0, 1, -1, -1, 0, -1, 1, 0]
y_moves = [1, 0, -1, 0, 0, 1, 0, -1, 0, 1]

# Running position, seeded with the starting point at the origin.
x_pos = [0]
y_pos = [0]

for i in range(len(x_moves)):
    # new position = previous position + this step's move
    x_pos.append(x_pos[-1] + x_moves[i])
    y_pos.append(y_pos[-1] + y_moves[i])

plt.plot(x_pos, y_pos, color='red', marker='^')  # red line, red triangles
plt.xlabel('x position')
plt.ylabel('y position')
plt.title('Task 1 - plotting lists')
plt.show()
