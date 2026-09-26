# AS GIVEN on the test sheet - has 3 bugs students must find (Activity 2.1)
# 1. `==` should be `=` (comparison instead of assignment)
# 2. missing `:` after the for statement
# 3. the print always shows the same fixed string - doesn't use pos/spacing

num_students = 5
num_steps == 10

for t in range(num_steps)
    print("S S S S S")
