import random
import matplotlib.pyplot as plt

epsilon_start = 0.9
epsilon_decay = 0.9387
epsilon_min = 0.02

iterations = 60
start_step = 0

num_combos = 6480
max_std = num_combos / 5

best_combo_index = 688

steps = []
indices = []

for step in range(start_step, iterations):

    epsilon = max(epsilon_min, epsilon_start * (epsilon_decay ** step))
    std_dev = max_std * epsilon

    rand_index = int(random.gauss(best_combo_index, std_dev))

    # clamp to valid range
    rand_index = max(0, min(num_combos - 1, rand_index))

    steps.append(step)
    indices.append(rand_index)

# Plot
plt.figure(figsize=(12,6))
plt.plot(steps, indices, marker='o', linestyle='-')
plt.xlabel("Step")
plt.ylabel("Index")
plt.title("Selected Index vs Step")
plt.grid(True)
plt.show()