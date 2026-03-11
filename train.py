import numpy as np
import subprocess
import random
import json

## TopLeft, TopRight, BottomLeft, BottomRight Coordinate of Map
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

#### POSSIBLE DEFENSE STRUCTURE POSITIONING
grid = generate_grid_centers_numpy(TL, TR, BL, BR, 12, 12)

# print(grid.shape)
# print(grid[0,0])

def_builds = grid.reshape(-1,2).tolist()
# print(len(def_builds))

#### POSSIBLE ARMY OFFENSIVE POSITIONING
def generate_3x3_grid_numpy(center, dx, dy):
    x, y = center

    xs = np.array([x - dx, x, x + dx])
    ys = np.array([y + dy, y, y - dy])

    X, Y = np.meshgrid(xs, ys)

    grid = np.stack((X, Y), axis=2)

    return grid

center = grid[0,0]
dx = 3
dy = 3

# offensive_pos = generate_3x3_grid_numpy(center, dx, dy)
# print(offensive_pos)

#### INDUSTRY 1 of 5 options
chengdu = [94.6, 75.7]
shanghai = [108.7, 83.7]
hanoi = [98.5, 67.7]
moscow = [79.4, 94.6]
delhi = [83.5, 65.0]

war_industry_options = [chengdu, shanghai, hanoi, moscow, delhi]

#### FINAL ATTACK
english_channel = [50, 87]

### 1 TIME SIMULATION with RANDOM Decisive Battles and War Industry Placements
option_index = random.randint(0,4)
option = np.array(war_industry_options[option_index]).astype(int)

def_pos = random.randint(0, 143)
def_build = np.array(def_builds[def_pos]).astype(int)

offensive_grid = generate_3x3_grid_numpy(def_build , dx, dy)
offensive_pts = offensive_grid.reshape(-1,2).tolist()
offensive_pt = np.array(offensive_pts[0]).astype(int)

# print("INDUSTRY AT ", option)
# print("DEFFENSIVE BUILDS AT", def_build)
# print("OFFENSIVE POS", offensive_pt)
# print("FINAL OFFENSIVE", english_channel)
# print("################################")

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

print("Captured JSON:")
print(json_results)


### RL CLIMB to FIND BEST Decisive Battles and War Industries Placements

# sim_cal = 0
# for option in war_industry_options:
#     for def_build in def_builds:
#         offensive_grid = generate_3x3_grid_numpy(def_build , dx, dy)
#         offensive_pts = offensive_grid.reshape(-1,2).tolist()

#         for offensive_pt in offensive_pts:
#             sim_cal += 1
#             print("SIMULATION ", sim_cal)
#             print("INDUSTRY AT ", option)
#             print("DEFFENSIVE BUILDS AT", def_build)
#             print("OFFENSIVE POS", offensive_pt)
#             print("FINAL OFFENSIVE", english_channel)
#             print("################################")

            # cmd = [
            #     "python",
            #     "./worldwar_sim.py",
            #     "--ComputerRace", "Random",
            #     "--ComputerDifficulty", "VeryHard",
            #     "--Map", "WorldWar",
            #     "--Industry", option,
            #     "--Offense", offensive_pt,
            #     "--Defense", def_build,
            #     "--Final", english_channel
            # ]

            # subprocess.run(cmd)






