import numpy as np
import subprocess
import random
import json
import os
import matplotlib.pyplot as plt

def plot_reward_progress(filename="battle_stats.json", output="fibonnaci_reward_progress.png"):

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

#############################################################
# HYBRID TRAINER WITH TRUE ROLLBACK ON CRASH
# - 12 random steps
# - 48 fibonacci steps
# - if crash during a step -> resume same step next run
#############################################################

import copy
import json
import random

state_file = "training_state.json"

num_combos = len(combos)

random_steps = 12
fibon_steps = 48
iterations = random_steps + fibon_steps

# =====================================================
# LOAD / INIT
# =====================================================
try:
    with open(state_file, "r") as f:
        state = json.load(f)

    tested_rewards   = state["tested_rewards"]
    best_reward      = state["best_reward"]
    best_combo_index = state["best_combo_index"]
    left             = state["left"]
    right            = state["right"]
    fib              = state["fib"]
    fib_index        = state["fib_index"]
    start_step       = state["step"]     # IMPORTANT: same step resumes

    print("Recovered state")
    print("Resume at step:", start_step)

except:

    tested_rewards = {}
    best_reward = -999999
    best_combo_index = None

    left = 0
    right = num_combos - 1

    fib = [1, 1]
    while fib[-1] < num_combos:
        fib.append(fib[-1] + fib[-2])

    fib_index = len(fib) - 1
    start_step = 0

    print("Fresh training")


# =====================================================
# SAVE SNAPSHOT
# =====================================================
def save_state(step):
    state = {
        "step": step,                 # current step, not next step
        "tested_rewards": tested_rewards,
        "best_reward": best_reward,
        "best_combo_index": best_combo_index,
        "left": left,
        "right": right,
        "fib": fib,
        "fib_index": fib_index
    }

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


# =====================================================
# SAVE COMPLETED STEP
# =====================================================
def save_after_success(step):
    state = {
        "step": step + 1,            # next step only after success
        "tested_rewards": tested_rewards,
        "best_reward": best_reward,
        "best_combo_index": best_combo_index,
        "left": left,
        "right": right,
        "fib": fib,
        "fib_index": fib_index
    }

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


# =====================================================
# EVALUATE
# =====================================================
def evaluate_combo(combo_index):

    global best_reward, best_combo_index

    key = str(combo_index)

    if key in tested_rewards:
        return tested_rewards[key]

    combo = combos[combo_index]

    print("Testing combo:", combo_index)

    battle_stats = simulate_battle(
        combo["Industry"],
        combo["Defensive_Pos"],
        combo["Offensive_Pos"]
    )

    battle_stats["combo_index"] = combo_index

    append_json("battle_stats.json", battle_stats)
    plot_reward_progress()

    reward = (
        battle_stats["Battle_Score"]
        - 0.3 * battle_stats["Battle_STD"]
    )

    tested_rewards[key] = reward

    if reward > best_reward:
        best_reward = reward
        best_combo_index = combo_index

    print("Reward:", reward)
    return reward


# =====================================================
# MAIN LOOP
# =====================================================
for step in range(start_step, iterations):

    print("\n====================")
    print("STEP", step)

    # snapshot memory before step starts
    snapshot = {
        "tested_rewards": copy.deepcopy(tested_rewards),
        "best_reward": best_reward,
        "best_combo_index": best_combo_index,
        "left": left,
        "right": right,
        "fib_index": fib_index
    }

    # save disk snapshot before work
    save_state(step)

    try:

        #################################################
        # RANDOM PHASE
        #################################################
        if step < random_steps + 1:

            print("MODE: RANDOM")

            while True:
                combo_index = random.randint(0, num_combos - 1)
                if str(combo_index) not in tested_rewards:
                    break

            evaluate_combo(combo_index)

            #################################################
            # AFTER LAST RANDOM STEP:
            # FIND TOP SCORES FROM battle_stats.json
            # BUILD FIB RANGE FROM TOP 2
            #################################################
            if step == random_steps:

                try:
                    with open("battle_stats.json", "r") as f:
                        history = json.load(f)
                except:
                    history = []

                ranked = []

                for row in history:

                    idx = row.get("combo_index", None)

                    if idx is None:
                        continue

                    reward = row["Battle_Score"]
                    ranked.append((idx, reward))

                # remove duplicate combo_index keep highest score
                best_per_index = {}

                for idx, reward in ranked:
                    if idx not in best_per_index:
                        best_per_index[idx] = reward
                    else:
                        best_per_index[idx] = max(
                            best_per_index[idx],
                            reward
                        )

                ranked = sorted(
                    best_per_index.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                #################################################
                # TOP 2 SCORES
                #################################################
                top1 = int(ranked[0][0])
                top2 = int(ranked[1][0])

                left = min(top1, top2)
                right = max(top1, top2)

                # if too narrow, widen slightly
                if left == right:
                    left = max(0, left - 1)
                    right = min(num_combos - 1, right + 1)

                #################################################
                # REBUILD FIB ARRAY
                #################################################
                span = right - left + 1

                fib = [1, 1]
                while fib[-1] < span:
                    fib.append(fib[-1] + fib[-2])

                fib_index = len(fib) - 1

                #################################################
                # RESET FIB MEMORY
                #################################################

                top_reward_index = 0 if top1 == left else 1

                print(
                    "ANCHOR INDEX ", left, 
                    "\nANCHOR REWARD ", ranked[top_reward_index][1]
                )

                state["prev_index"] = left
                state["prev_reward"] = ranked[top_reward_index][1]
                state["prev_dir"] = 1

                print("TOP RANDOM #1:", top1, ranked[0][1])
                print("TOP RANDOM #2:", top2, ranked[1][1])
                print("NEW FIB RANGE:", left, "to", right)
                print("RANKED ", ranked)

        #################################################
        # FIBONACCI PHASE
        # Use PREVIOUS STEP reward + one new probe only
        # instead of testing x1 and x2 every step
        #################################################
        else:

            print("MODE: FIBONACCI")
            print("Range:", left, right)

            if right - left > 2 and fib_index >= 2:
                print("FIBON ALGO WITHIN RANGE ", left, right)
                
                span = right - left
                print("SPAN ", span)

                ### FIBON IMROVEMENT STEPS
                prev_index = state["prev_index"] 
                prev_reward = state["prev_reward"]

                ## choose mirrored fibonacci candidate
                if prev_index <= (left + right) / 2:
                    next_index = left + fib[fib_index - 1]
                else:
                    next_index = right - fib[fib_index - 1]

                next_index = min(max(left + 1, next_index), right - 1)

                print("Improving Fibon Step at index ", next_index)

                if next_index == prev_index:
                    next_index = left + span // 2

                print("Previous Probe:", prev_index, prev_reward)
                print("Next Probe:", next_index)

                next_reward = evaluate_combo(next_index)

                if next_reward > prev_reward:
                    print("New probe stronger")

                    if next_index > prev_index:
                        left = prev_index
                    else:
                        right = prev_index

                    prev_index = next_index
                    prev_reward = next_reward

                else:

                    print("Previous probe stronger")

                    if next_index > prev_index:
                        right = next_index
                    else:
                        left = next_index

                fib_index -= 1
               
                # #################################################
                # # SAVE probe memory into state
                # #################################################
                state["prev_index"] = prev_index
                state["prev_reward"] = prev_reward

                print("New Range:", left, right)
                print("Carry Forward Best Probe:", prev_index, prev_reward)

            else:
                print("Range exhausted")
                break

        # step finished successfully
        save_after_success(step)

    except Exception as e:

        print("Crash detected:", e)
        print("Rolling back step", step)

        # restore memory snapshot
        tested_rewards   = snapshot["tested_rewards"]
        best_reward      = snapshot["best_reward"]
        best_combo_index = snapshot["best_combo_index"]
        left             = snapshot["left"]
        right            = snapshot["right"]
        fib_index        = snapshot["fib_index"]

        # save rolled back state
        save_state(step)

        raise


# =====================================================
# FINAL
# =====================================================
print("\n====================")
print("BEST RESULT")

if best_combo_index is not None:
    print("Index:", best_combo_index)
    print("Reward:", best_reward)
    print(combos[best_combo_index])