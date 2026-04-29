import math
import matplotlib.pyplot as plt

# ---------------------------------
# Generate Fibonacci Spiral Samples
# ---------------------------------
fib = [1, 1]

# build Fibonacci sequence
for _ in range(10):
    fib.append(fib[-1] + fib[-2])

print(fib)

# store coordinates
x_vals = [0]
y_vals = [0]

angle = 0  # radians

for r in fib:
    x = r * math.cos(angle)
    y = r * math.sin(angle)

    x_vals.append(x)
    y_vals.append(y)

    # golden angle approximation
    angle += math.pi / 2

# ---------------------------------
# Plot Spiral Points
# ---------------------------------
plt.figure(figsize=(8,8))
plt.plot(x_vals, y_vals, marker='o', linestyle='-')

# label each Fibonacci number
for i in range(1, len(x_vals)):
    plt.text(x_vals[i], y_vals[i], str(fib[i-1]), fontsize=10)

plt.title("Sample Fibonacci Spiral")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.axis("equal")
plt.show()