import numpy as np
import subprocess
import random
import json
import os
import matplotlib.pyplot as plt
import pathlib

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel


###################################
# PATHS
###################################

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
SIM_PATH = ROOT_DIR / "worldwar_sim.py"

state_file = "training_state.json"
stats_file = "battle_stats.json"


###################################
# PLOT REWARD PROGRESS
###################################

def plot_reward_progress():

    try:
        with open(stats_file) as f:
            data = json.load(f)
    except:
        return

    rewards=[]
    best_rewards=[]
    best=-999999

    for entry in data:

        reward = entry["Battle_Score"] - 0.3*entry["Battle_STD"]

        rewards.append(reward)

        best=max(best,reward)
        best_rewards.append(best)

    iterations=list(range(1,len(rewards)+1))

    plt.figure(figsize=(8,5))

    plt.plot(iterations,rewards,marker="o",label="Reward")
    plt.plot(iterations,best_rewards,linewidth=3,label="Best So Far")

    plt.xlabel("Iteration")
    plt.ylabel("Reward")
    plt.title("Battle Optimization Progress")

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig("reward_progress.png")
    plt.close()


###################################
# INDUSTRY OPTIONS
###################################

chengdu=[94.6,75.7]
shanghai=[108.7,83.7]
hanoi=[98.5,67.7]
moscow=[79.4,94.6]
delhi=[83.5,65.0]

war_industry_options=[chengdu,shanghai,hanoi,moscow,delhi]


###################################
# DEFENSE GRID
###################################

TL=[74.1,93.7]
TR=[114.0,94.4]
BL=[77.5,48.8]
BR=[100.5,49.0]

def generate_grid_centers_numpy(TL,TR,BL,BR,rows,cols):

    TL=np.array(TL)
    TR=np.array(TR)
    BL=np.array(BL)
    BR=np.array(BR)

    u=(np.arange(cols)+0.5)/cols
    v=(np.arange(rows)+0.5)/rows

    U,V=np.meshgrid(u,v)

    grid=((1-U)*(1-V))[...,None]*TL + \
         (U*(1-V))[...,None]*TR + \
         ((1-U)*V)[...,None]*BL + \
         (U*V)[...,None]*BR

    return grid

grid=generate_grid_centers_numpy(TL,TR,BL,BR,12,12)
def_builds=grid.reshape(-1,2).tolist()


###################################
# OFFENSE GRID
###################################

def generate_3x3_grid_numpy(center,dx,dy):

    x,y=center

    xs=np.array([x-dx,x,x+dx])
    ys=np.array([y+dy,y,y-dy])

    X,Y=np.meshgrid(xs,ys)

    grid=np.stack((X,Y),axis=2)

    return grid

dx=3
dy=3


###################################
# GENERATE ALL COMBOS
###################################

combos=[]

for industry in war_industry_options:

    for defense in def_builds:

        offensive_grid=generate_3x3_grid_numpy(defense,dx,dy)

        offensive_pts=offensive_grid.reshape(-1,2).tolist()

        for offense in offensive_pts:

            combos.append({
                "Industry":[int(industry[0]),int(industry[1])],
                "Defensive_Pos":[int(defense[0]),int(defense[1])],
                "Offensive_Pos":[int(offense[0]),int(offense[1])]
            })

print("Total combos:",len(combos))

num_combos=len(combos)


###################################
# FEATURE MATRIX
###################################

def combo_to_features(combo):

    return [
        combo["Industry"][0],
        combo["Industry"][1],
        combo["Defensive_Pos"][0],
        combo["Defensive_Pos"][1],
        combo["Offensive_Pos"][0],
        combo["Offensive_Pos"][1]
    ]

X_all=np.array([combo_to_features(c) for c in combos])


###################################
# LOAD TRAINING DATA
###################################

def load_training_data():

    try:
        with open(stats_file) as f:
            data=json.load(f)
    except:
        return np.array([]),np.array([]),[]

    X=[]
    y=[]
    tested=[]

    for entry in data:

        reward = entry["Battle_Score"] - 0.3*entry["Battle_STD"]

        idx=entry["combo_index"]

        X.append(X_all[idx])
        y.append(reward)
        tested.append(idx)

    return np.array(X),np.array(y),tested


###################################
# STATE MANAGEMENT
###################################

def load_state():

    try:

        with open(state_file) as f:
            state=json.load(f)

        iteration=state["iteration"]
        best_reward=state["best_reward"]
        best_combo_index=state["best_combo_index"]
        tested_indices=set(state["tested_indices"])

        print("Resuming training from iteration",iteration)

    except:

        iteration=0
        best_reward=-999999
        best_combo_index=None
        tested_indices=set()

        print("Starting fresh training")

    return iteration,best_reward,best_combo_index,tested_indices


def save_state(iteration,best_reward,best_combo_index,tested_indices):

    state={
        "iteration":iteration,
        "best_reward":best_reward,
        "best_combo_index":best_combo_index,
        "tested_indices":list(tested_indices)
    }

    with open(state_file,"w") as f:
        json.dump(state,f,indent=2)


###################################
# GAUSSIAN MODEL
###################################

def train_model(X,y):

    kernel=ConstantKernel(1.0)*RBF(length_scale=10)

    model=GaussianProcessRegressor(
        kernel=kernel,
        alpha=1e-6,
        normalize_y=True
    )

    model.fit(X,y)

    return model


###################################
# SELECT NEXT COMBO
###################################

def select_next_combo(model, tested):

    candidate_size = 300

    candidates = np.random.choice(len(X_all), candidate_size, replace=False)

    mu, sigma = model.predict(X_all[candidates], return_std=True)

    kappa = 2.0
    acquisition = mu + kappa * sigma

    best_local = candidates[np.argmax(acquisition)]

    if best_local in tested:
        remaining = list(set(range(len(X_all))) - tested)
        best_local = random.choice(remaining)

    return int(best_local)


###################################
# SIMULATE BATTLE
###################################

def simulate_battle(option,def_build,offensive_pt):

    english_channel=[50,87]

    cmd=[
        "python","-u",str(SIM_PATH),
        "--ComputerRace","Random",
        "--ComputerDifficulty","VeryHard",
        "--Map","WorldWar",
        "--Industry",",".join(map(str,option)),
        "--Offense",",".join(map(str,offensive_pt)),
        "--Defense",",".join(map(str,def_build)),
        "--Final",",".join(map(str,english_channel))
    ]

    process=subprocess.Popen(
        cmd,
        cwd=str(ROOT_DIR),
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

    if len(json_results)<3:

        print("Simulation failed")

        return {
            "Industry":option,
            "Offensive_Pos":offensive_pt,
            "Defensive_Pos":def_build,
            "Battle_Score":-9999,
            "Battle_STD":9999
        }

    battle_scores=[
        json_results[0]["Battle Score"],
        json_results[1]["Battle Score"],
        json_results[2]["Battle Score"]
    ]

    avg=np.mean(battle_scores)
    std=np.std(battle_scores)

    return {
        "Industry":option,
        "Offensive_Pos":offensive_pt,
        "Defensive_Pos":def_build,
        "Simulation_1":json_results[0],
        "Simulation_2":json_results[1],
        "Simulation_3":json_results[2],
        "Battle_Score":float(avg),
        "Battle_STD":float(std)
    }


###################################
# APPEND JSON
###################################

def append_json(new_data):

    try:
        with open(stats_file) as f:
            data=json.load(f)
    except:
        data=[]

    data.append(new_data)

    with open(stats_file,"w") as f:
        json.dump(data,f,indent=2)


###################################
# OPTIMIZATION LOOP
###################################

iterations=60

start_iter,best_reward,best_combo_index,tested_indices=load_state()

print("\nStarting Bayesian Optimization")

for step in range(start_iter,iterations):

    print("\n======================")
    print("ITERATION",step)
    print("======================")

    X,y,_=load_training_data()

    print("Previous samples:",len(y))

    if len(y)<8:

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

    battle_stats=simulate_battle(
        combo["Industry"],
        combo["Defensive_Pos"],
        combo["Offensive_Pos"]
    )

    battle_stats["combo_index"]=combo_index

    append_json(battle_stats)

    tested_indices.add(combo_index)

    reward = battle_stats["Battle_Score"] - 0.3*battle_stats["Battle_STD"]

    if reward>best_reward:

        best_reward=reward
        best_combo_index=combo_index

    print("Reward:",reward)
    print("Best reward:",best_reward)

    plot_reward_progress()

    save_state(step+1,best_reward,best_combo_index,tested_indices)


###################################
# FINAL RESULT
###################################

print("\n======================")
print("BEST COMBO FOUND")
print("======================")

print("Index:",best_combo_index)
print("Reward:",best_reward)

if best_combo_index is not None:
    print(combos[best_combo_index])