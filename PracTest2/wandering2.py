"""
wandering2.py - COMP1005 Practical Test 2, Task 2

Sprint 2 goal: swap the lists for NumPy integer ARRAYS, and prove the
two approaches give the same walk by plotting them side by side.
"""
import numpy as np
import matplotlib.pyplot as plt

x_moves = [1, 0, 0, 1, -1, -1, 0, -1, 1, 0]
y_moves = [1, 0, -1, 0, 0, 1, 0, -1, 0, 1]

# --- Task 1 version, kept so it can go in the left-hand subplot ---------
x_pos = [0]
y_pos = [0]
for i in range(len(x_moves)):
    x_pos.append(x_pos[-1] + x_moves[i])
    y_pos.append(y_pos[-1] + y_moves[i])

# --- Task 2 version: arrays instead of lists ----------------------------
x_movearray = np.array(x_moves, dtype=int)
y_movearray = np.array(y_moves, dtype=int)

# one extra slot at index 0 for the starting position
x_posarray = np.zeros(len(x_movearray) + 1, dtype=int)
y_posarray = np.zeros(len(y_movearray) + 1, dtype=int)

for i in range(len(x_movearray)):
    x_posarray[i + 1] = x_posarray[i] + x_movearray[i]
    y_posarray[i + 1] = y_posarray[i] + y_movearray[i]

# --- subplots: list version left, array version right ------------------
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Task 2 - lists vs arrays')

ax1.plot(x_pos, y_pos, color='red', marker='^')
ax1.set_xlabel('x position')
ax1.set_ylabel('y position')
ax1.set_title('list version (Task 1)')

ax2.plot(x_posarray, y_posarray, color='purple', marker='D')
ax2.set_xlabel('x position')
ax2.set_ylabel('y position')
ax2.set_title('array version (Task 2)')

plt.show()
