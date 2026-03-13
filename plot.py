import json
import numpy as np
import matplotlib.pyplot as plt

# load json
with open("battle_stats.json", "r") as f:
    data = json.load(f)

industry = []
offensive = []
defensive = []
reward = []

for entry in data:

    # compute reward
    r = entry["Battle_Score"] - 0.3 * entry["Battle_STD"]
    reward.append(r)

    # compute center of coordinates
    industry.append(np.mean(entry["Industry"]))
    offensive.append(np.mean(entry["Offensive_Pos"]))
    defensive.append(np.mean(entry["Defensive_Pos"]))

fig = plt.figure(figsize=(9,7))
ax = fig.add_subplot(111, projection='3d')

# scatter points
sc = ax.scatter(
    industry,
    offensive,
    defensive,
    c=reward,
    s=120,
    cmap="viridis"
)

# optimizer path
ax.plot(
    industry,
    offensive,
    defensive,
    linewidth=2
)

# iteration labels
for i in range(len(industry)):
    ax.text(
        industry[i],
        offensive[i],
        defensive[i],
        str(i+1)
    )

ax.set_xlabel("Industry")
ax.set_ylabel("Offensive Position")
ax.set_zlabel("Defensive Position")

plt.colorbar(sc, label="Reward")

plt.title("3D Optimization Path")

plt.show()