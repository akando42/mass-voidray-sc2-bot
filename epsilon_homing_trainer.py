import numpy as np
import subprocess
import random
import json
import os
import matplotlib.pyplot as plt

def plot_reward_progress(filename="battle_stats.json", output="reward_progress.png"):

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except:
        return

    rewards = []
    best_rewards = []

    best = -999999

    for entry in data:

        mean_score = entry["Battle_Score"]
        std = entry["Battle_STD"]

        reward = mean_score - 0.3 * std
        rewards.append(reward)

        best = max(best, reward)
        best_rewards.append(best)

    iterations = list(range(1, len(rewards) + 1))

    plt.figure(figsize=(8,5))

    plt.plot(iterations, rewards, marker="o", label="Reward")
    plt.plot(iterations, best_rewards, linewidth=3, label="Best So Far")

    plt.xlabel("Iteration")
    plt.ylabel("Reward")
    plt.title("Battle Optimization Progress")

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig(output)
    plt.close()

###############################
### INDUSTRY 1 of 5 options ###
###############################

chengdu = [94.6, 75.7]
shanghai = [108.7, 83.7]
hanoi = [98.5, 67.7]
moscow = [79.4, 94.6]
delhi = [83.5, 65.0]

war_industry_options = [chengdu, shanghai, hanoi, moscow, delhi]

# option_index = random.randint(0,4)
# option = np.array(war_industry_options[option_index]).astype(int)


#####################
### DEFENSIVE POS ###
#####################

# TopLeft, TopRight, BottomLeft, BottomRight Coordinate of Map
TL = [74.1, 93.7]
TR = [114.0, 94.4]
BL = [77.5, 48.8]
BR = [100.5, 49.0]

def generate_grid_centers_numpy(TL, TR, BL, BR, rows, cols):
    TL = np.array(TL)
    TR = np.array(TR)
    BL = np.array(BL)
    BR = np.array(BR)

    # create normalized grid coordinates
    u = (np.arange(cols) + 0.5) / cols
    v = (np.arange(rows) + 0.5) / rows

    U, V = np.meshgrid(u, v)

    # bilinear interpolation
    grid = ((1-U)*(1-V))[...,None]*TL + \
           (U*(1-V))[...,None]*TR + \
           ((1-U)*V)[...,None]*BL + \
           (U*V)[...,None]*BR

    return grid

# POSSIBLE DEFENSE STRUCTURE POSITIONING
grid = generate_grid_centers_numpy(TL, TR, BL, BR, 12, 12)
def_builds = grid.reshape(-1,2).tolist()

# def_pos = random.randint(0, 143)
# def_build = np.array(def_builds[def_pos]).astype(int)


#####################
### OFFENSIVE POS ###
#####################

# POSSIBLE ARMY OFFENSIVE POSITIONING
def generate_3x3_grid_numpy(center, dx, dy):
    x, y = center

    xs = np.array([x - dx, x, x + dx])
    ys = np.array([y + dy, y, y - dy])

    X, Y = np.meshgrid(xs, ys)

    grid = np.stack((X, Y), axis=2)

    return grid

# Offensive POS
dx = 3
dy = 3

# offensive_grid = generate_3x3_grid_numpy(def_build , dx, dy)
# offensive_pts = offensive_grid.reshape(-1,2).tolist()
# offensive_index = random.randint(0,8)
# offensive_pt = np.array(offensive_pts[offensive_index]).astype(int)


#######################
### POSSIBLE COMBOS ###
#######################
combos = []

for industry in war_industry_options:
    for defense in def_builds:
        offensive_grid = generate_3x3_grid_numpy(defense , dx, dy)
        offensive_pts = offensive_grid.reshape(-1,2).tolist()

        for offense in offensive_pts:

            combo = {
                "Industry": [int(industry[0]), int(industry[1])],
                "Defensive_Pos": [int(defense[0]), int(defense[1])],
                "Offensive_Pos": [int(offense[0]), int(offense[1])]
            }

            combos.append(combo)

print("Total combos:", len(combos))

def simulate_battle(option, def_build, offensive_pt):
    print("INDUSTRY AT ", option)
    print("DEFFENSIVE BUILDS AT", def_build)
    print("OFFENSIVE POS", offensive_pt)

    #### FINAL ATTACK
    english_channel = [50, 87]    
   
    print("FINAL OFFENSIVE", english_channel)
    print("################################")

    cmd = [
        "python",
        "-u",
        "./worldwar_sim.py",
        "--ComputerRace", "Random",
        "--ComputerDifficulty", "VeryHard",
        "--Map", "WorldWar",
        "--Industry", ",".join(map(str, option)),
        "--Offense", ",".join(map(str, offensive_pt)),
        "--Defense", ",".join(map(str, def_build)),
        "--Final", ",".join(map(str, english_channel))
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output_lines = []
    json_results = []

    for line in process.stdout:
        print(line, end="")              # still show terminal output
        output_lines.append(line)

        # detect JSON line
        line_clean = line.strip()
        if line_clean.startswith("{") and "army_strength" in line_clean:
            try:
                data = json.loads(line_clean)
                json_results.append(data)
            except json.JSONDecodeError:
                pass

    process.wait()

    output = "".join(output_lines)

    # print("Captured JSON:")
    # print(json_results)

    battle_scores = [
        json_results[0]["Battle Score"], 
        json_results[1]["Battle Score"], 
        json_results[2]["Battle Score"]
    ]

    battle_average_score = np.mean(battle_scores)
    battle_std = np.std(battle_scores)

    battle_stats = {
        "Industry": option,
        "Offensive_Pos": offensive_pt,
        "Defensive_Pos": def_build,
        "Simulation_1": json_results[0],
        "Simulation_2": json_results[1],
        "Simulation_3": json_results[2],
        "Battle_Score": float(battle_average_score),
        "Battle_STD": float(battle_std)
    }

    print(battle_stats)
    return battle_stats

def append_json(filename, new_data):

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(new_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


### ONE TIME SIMULATION
# combos_index = random.randint(0, 6479)
# combo = combos[combos_index]

# print("SELECTED COMBO ")
# print(combo['Industry'])
# print(combo['Defensive_Pos'])
# print(combo['Offensive_Pos'])

# battle_stats = simulate_battle(
#     combo['Industry'], 
#     combo['Defensive_Pos'], 
#     combo['Offensive_Pos']
# )

# append_json("battle_stats.json", battle_stats)

# mean_score = battle_stats["Battle_Score"]
# std = battle_stats["Battle_STD"]
# reward = mean_score - 0.3 * std

# print("Battle Reward ", reward)


#############################
### RL COMBO OPTIMIZATION ###
#############################

state_file = "training_state.json"

num_combos = len(combos)

# ----------------------------
# LOAD TRAINING STATE
# ----------------------------
try:
    with open(state_file, "r") as f:
        state = json.load(f)

    Q = np.array(state["Q"])
    N = np.array(state["N"])
    best_reward = state["best_reward"]
    best_combo_index = state["best_combo_index"]
    start_step = state["step"] + 1

    print("Resuming training from step", start_step)

except (FileNotFoundError, json.JSONDecodeError):

    Q = np.zeros(num_combos)
    N = np.zeros(num_combos)

    best_reward = -999999
    best_combo_index = None
    start_step = 0

    print("Starting fresh training")

# ----------------------------
# RL PARAMETERS
# ----------------------------

epsilon_start = 0.9
epsilon_decay = 0.9387
epsilon_min = 0.1
iterations = 60

# ----------------------------
# TRAINING LOOP
# ----------------------------

for step in range(start_step, iterations):

    epsilon = max(epsilon_min, epsilon_start * (epsilon_decay ** step))
    std_dev = max(1, (num_combos / 4) * epsilon)

    print("\n=== ITERATION", step, "===")
    print("epsilon:", round(epsilon, 4))

    # explore vs exploit
    if random.random() < epsilon:
        combo_index = random.randint(0, num_combos - 1)

    else:
        top_k = 10
        top_indices = np.argsort(Q)[-top_k:]
        anchor = random.choice(top_indices)

        combo_index = int(random.gauss(anchor, std_dev))
        combo_index = max(0, min(num_combos - 1, combo_index))

        print("MODE: EXPLOIT")
        
    combo = combos[combo_index]

    print("Testing combo index:", combo_index)

    battle_stats = simulate_battle(
        combo['Industry'],
        combo['Defensive_Pos'],
        combo['Offensive_Pos']
    )

    battle_stats["combo_index"] = combo_index

    append_json("battle_stats.json", battle_stats)

    plot_reward_progress()

    mean_score = battle_stats["Battle_Score"]
    std = battle_stats["Battle_STD"]
    reward = mean_score - 0.3 * std

    print("Reward:", reward)

    # update bandit stats
    N[combo_index] += 1
    Q[combo_index] += (reward - Q[combo_index]) / N[combo_index]

    # track best combo
    if reward > best_reward:
        best_reward = reward
        best_combo_index = combo_index

    print("Best reward so far:", best_reward)
    print("Best combo index:", best_combo_index)

    # ----------------------------
    # SAVE TRAINING STATE
    # ----------------------------
    state = {
        "step": step,
        "Q": Q.tolist(),
        "N": N.tolist(),
        "best_reward": best_reward,
        "best_combo_index": best_combo_index
    }

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

# ----------------------------
# FINAL RESULT
# ----------------------------

print("\n======================")
print("FINAL BEST COMBO")
print("Index:", best_combo_index)
print("Reward:", best_reward)
print(combos[best_combo_index])