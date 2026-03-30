import random

epsilon_start = 0.9
epsilon_decay = 0.9387
epsilon_min = 0.02

iterations = 60
start_step = 0

num_combos = 6480
max_std = num_combos / 5

best_combo_index = 688

for step in range(start_step, iterations):

	epsilon = max(epsilon_min, epsilon_start * (epsilon_decay ** step))

	std_dev = max_std * epsilon  # controls spread

	rand_index = int(random.gauss(best_combo_index, std_dev))

	# clamp to valid range
	rand_index = max(0, min(num_combos - 1, rand_index))
	# print("STD DEV ", std_dev)
	print("SELECT INDEX ", rand_index)