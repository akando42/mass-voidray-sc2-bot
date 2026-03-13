import numpy as np
import subprocess
import random
import json
import os
import matplotlib.pyplot as plt

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel


#################################
### PLOT REWARD PROGRESS PNG ###
#################################

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

        reward = entry["Battle_Score"] - 0.3 * entry["Battle_STD"]

        rewards.append(reward)

        best = max(best, reward)
        best_rewards.append(best)

    iterations = list(range(1, len(rewards)+1))

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
### INDUSTRY OPTIONS (5) ###
###############################

chengdu = [94.6, 75.7]
shanghai = [108.7, 83.7]
hanoi = [98.5, 67.7]
moscow = [79.4, 94.6]
delhi = [83.5, 65.0]

war_industry_options = [chengdu, shanghai, hanoi, moscow, delhi]


##############################
### DEFENSIVE GRID (12x12) ###
##############################

TL = [74.1, 93.7]
TR = [114.0, 94.4]
BL = [77.5, 48.8]
BR = [100.5, 49.0]

def generate_grid_centers_numpy(TL, TR, BL, BR, rows, cols):

    TL = np.array(TL)
    TR = np.array(TR)
    BL = np.array(BL)
    BR = np.array(BR)

    u = (np.arange(cols)+0.5)/cols
    v = (np.arange(rows)+0.5)/rows

    U, V = np.meshgrid(u,v)

    grid = ((1-U)*(1-V))[...,None]*TL + \
           (U*(1-V))[...,None]*TR + \
           ((1-U)*V)[...,None]*BL + \
           (U*V)[...,None]*BR

    return grid

grid = generate_grid_centers_numpy(TL,TR,BL,BR,12,12)
def_builds = grid.reshape(-1,2).tolist()


##############################
### OFFENSIVE GRID (3x3) ###
##############################

def generate_3x3_grid_numpy(center, dx, dy):

    x,y = center

    xs = np.array([x-dx,x,x+dx])
    ys = np.array([y+dy,y,y-dy])

    X,Y = np.meshgrid(xs,ys)

    grid = np.stack((X,Y),axis=2)

    return grid


dx = 3
dy = 3


###########################
### GENERATE ALL COMBOS ###
###########################

combos = []

for industry in war_industry_options:

    for defense in def_builds:

        offensive_grid = generate_3x3_grid_numpy(defense,dx,dy)

        offensive_pts = offensive_grid.reshape(-1,2).tolist()

        for offense in offensive_pts:

            combo = {
                "Industry":[int(industry[0]),int(industry[1])],
                "Defensive_Pos":[int(defense[0]),int(defense[1])],
                "Offensive_Pos":[int(offense[0]),int(offense[1])]
            }

            combos.append(combo)

print("Total combos:",len(combos))

num_combos = len(combos)


##############################
### FEATURE MATRIX FOR BO ###
##############################

def combo_to_features(combo):

    return [
        combo["Industry"][0],
        combo["Industry"][1],
        combo["Defensive_Pos"][0],
        combo["Defensive_Pos"][1],
        combo["Offensive_Pos"][0],
        combo["Offensive_Pos"][1]
    ]

X_all = np.array([combo_to_features(c) for c in combos])


############################
### LOAD TRAINING DATA ###
############################

def load_training_data(filename="battle_stats.json"):

    try:
        with open(filename) as f:
            data = json.load(f)
    except:
        return np.array([]),np.array([]),[]

    X=[]
    y=[]
    tested_indices=[]

    for entry in data:

        reward = entry["Battle_Score"] - 0.3*entry["Battle_STD"]

        idx = entry["combo_index"]

        X.append(X_all[idx])
        y.append(reward)

        tested_indices.append(idx)

    return np.array(X),np.array(y),tested_indices


###########################
### GAUSSIAN MODEL ###
###########################

def train_model(X,y):

    kernel = ConstantKernel(1.0)*RBF(length_scale=10)

    model = GaussianProcessRegressor(
        kernel=kernel,
        alpha=1e-6,
        normalize_y=True
    )

    model.fit(X,y)

    return model


###########################
### UCB ACQUISITION ###
###########################

def select_next_combo(model,tested_indices):

    mu,sigma = model.predict(X_all,return_std=True)

    kappa = 2.0

    acquisition = mu + kappa*sigma

    acquisition[tested_indices] = -999999

    return int(np.argmax(acquisition))


###########################
### BATTLE SIMULATION ###
###########################

def simulate_battle(option,def_build,offensive_pt):

    english_channel = [50,87]

    cmd = [
        "python","-u","../worldwar_sim.py",
        "--ComputerRace","Random",
        "--ComputerDifficulty","VeryHard",
        "--Map","WorldWar",
        "--Industry",",".join(map(str,option)),
        "--Offense",",".join(map(str,offensive_pt)),
        "--Defense",",".join(map(str,def_build)),
        "--Final",",".join(map(str,english_channel))
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    json_results=[]

    for line in process.stdout:

        print(line,end="")

        line_clean=line.strip()

        if line_clean.startswith("{") and "army_strength" in line_clean:

            try:
                data=json.loads(line_clean)
                json_results.append(data)
            except:
                pass

    process.wait()

    battle_scores=[
        json_results[0]["Battle Score"],
        json_results[1]["Battle Score"],
        json_results[2]["Battle Score"]
    ]

    avg=np.mean(battle_scores)
    std=np.std(battle_scores)

    battle_stats={
        "Industry":option,
        "Offensive_Pos":offensive_pt,
        "Defensive_Pos":def_build,
        "Simulation_1":json_results[0],
        "Simulation_2":json_results[1],
        "Simulation_3":json_results[2],
        "Battle_Score":float(avg),
        "Battle_STD":float(std)
    }

    return battle_stats


###########################
### APPEND JSON ###
###########################

def append_json(filename,new_data):

    try:
        with open(filename,"r") as f:
            data=json.load(f)
    except:
        data=[]

    data.append(new_data)

    with open(filename,"w") as f:
        json.dump(data,f,indent=2)


##################################
### BAYESIAN OPTIMIZATION LOOP ###
##################################

iterations = 60

print("\nStarting Bayesian Optimization")

for step in range(iterations):

    print("\n======================")
    print("ITERATION",step)
    print("======================")

    X,y,tested_indices = load_training_data()

    print("Previous samples:",len(y))

    # warmup random
    if len(y) < 8:

        combo_index=random.randint(0,num_combos-1)

        print("MODE: RANDOM")

    else:

        model=train_model(X,y)

        combo_index=select_next_combo(model,tested_indices)

        print("MODE: BAYESIAN UCB")

    if combo_index in tested_indices:

        print("Already tested - skipping")
        continue

    combo=combos[combo_index]

    print("Testing combo:",combo_index)

    battle_stats = simulate_battle(
        combo["Industry"],
        combo["Defensive_Pos"],
        combo["Offensive_Pos"]
    )

    battle_stats["combo_index"]=combo_index

    append_json("battle_stats.json",battle_stats)

    plot_reward_progress()

    reward = battle_stats["Battle_Score"] - 0.3*battle_stats["Battle_STD"]

    print("Reward:",reward)

print("\nOptimization Complete")