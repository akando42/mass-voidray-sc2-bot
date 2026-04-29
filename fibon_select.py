import matplotlib.pyplot as plt

# ----------------------------------
# SETTINGS
# ----------------------------------
iterations = 60
num_combos = 6480
best_combo_index = 688   # hidden optimum for demo

steps = []
indices = []
scores = []

# ----------------------------------
# OBJECTIVE FUNCTION
# Replace this with your real score
# ----------------------------------
def objective(index):
    # highest value at best_combo_index
    return -(index - best_combo_index) ** 2 + 100000


# ----------------------------------
# FIBONACCI SEARCH
# ----------------------------------
def fibonacci_search(left, right, max_iter):

    # build fibonacci sequence
    fib = [0, 1]
    while fib[-1] < (right - left):
        fib.append(fib[-1] + fib[-2])

        print(fib)

    n = len(fib) - 1

    x1 = left + fib[n - 2]
    x2 = left + fib[n - 1]

    f1 = objective(x1)
    f2 = objective(x2)

    step = 0

    while n > 2 and step < max_iter:

        steps.append(step)

        if f1 < f2:
            # best is toward right side
            left = x1
            steps.append(step)
            indices.append(x2)
            scores.append(f2)

            x1 = x2
            f1 = f2

            x2 = left + fib[n - 1]
            if x2 >= right:
                x2 = right - 1

            f2 = objective(x2)

        else:
            # best is toward left side
            right = x2
            indices.append(x1)
            scores.append(f1)

            x2 = x1
            f2 = f1

            x1 = left + fib[n - 2]
            if x1 <= left:
                x1 = left + 1

            f1 = objective(x1)

        n -= 1
        step += 1

    best_index = x1 if f1 > f2 else x2
    best_score = max(f1, f2)

    return best_index, best_score


# ----------------------------------
# RUN SEARCH
# ----------------------------------
best_idx, best_score = fibonacci_search(0, num_combos, iterations)

print("Best Index Found:", best_idx)
print("Best Score:", best_score)

# ----------------------------------
# PLOT SEARCH PATH
# ----------------------------------
plt.figure(figsize=(12,6))
plt.plot(range(len(indices)), indices, marker='o')
plt.axhline(best_combo_index, linestyle='--', label='True Best Index')
plt.xlabel("Step")
plt.ylabel("Tested Index")
plt.title("Fibonacci Search Converging to Optimal Index")
plt.grid(True)
plt.legend()
plt.show()