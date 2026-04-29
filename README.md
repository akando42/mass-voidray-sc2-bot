# Mass Void Ray SC2 Bot

![mass_voidray](https://user-images.githubusercontent.com/1859661/221099915-3649a58d-b340-469f-a6d1-8a799dfcaa11.gif)

<a href="https://www.youtube.com/watch?v=s_1qc8j0Xv4">
  DEMO
</a>

```
### Starcraft Map Locations
$ open /Applications/StarCraft\ II/Maps/Hanoi.SC2Map /

### Starting the Game
$ python ./go.py --ComputerRace Random --ComputerDifficulty VeryHard --Map DiscoBloodbathLE --Realtime


### Starting IndoChina Simulation
$ python ./indochina_sim.py --ComputerRace Random --ComputerDifficulty VeryHard --Map IndoChina 

### Starting World War Simulation
$ python ./worldwar_sim.py --ComputerRace Random --ComputerDifficulty VeryHard --Map WorldWar --Industry "104,74" --Offense "88,79" --Defense "88,73" --Final "50, 87"
```

### RL Discovered Best Solution

Epsilon Greedy
```
$ python ./worldwar_sim.py --ComputerRace Random --ComputerDifficulty VeryHard --Map WorldWar --Industry "94,75" --Offense "87,69" --Defense "87,69" --Final "50, 87"
```

Baynesian Optimizer
```
$ python ./worldwar_sim.py --ComputerRace Random --ComputerDifficulty VeryHard --Map WorldWar --Industry "94,75" --Offense "87,72" --Defense "84,69" --Final "50, 87"
```

Decaying Epsilon Around TopK
```
$ python ./worldwar_sim.py --ComputerRace Random --ComputerDifficulty VeryHard --Map WorldWar --Industry "98,67" --Offense "87,65" --Defense "84, 65" --Final "50, 87"
```

### GRID 
```
[74.1, 93.7]   [114.0, 94.4]
[77.5, 48.8]   [100.5, 49.0]
```
### ALGO Approaches
[X] 60 Iteration Epsilon Specs
[X] Decaying Epsilon Around Highest Reward

[ ] Fibonacci Optimization Algorithm

```
epsilon_start = 0.9
epsilon_decay = 0.9387
epsilon_min = 0.02
```

****
Rewrite FIBONACCI PHASE add More Prior Random  
Keep Best Reward as the same if FIBON do not reach new high 
****


### Multi Pronged Feigned Retreat Attack From Western Force 
```
python ./west_vs_east.py \
--Map MultiprongedAttacks \
--Industry "104,74" \
--Offense "88,79" \
--Defense "88,73" \
--Final "50,87" \
--EnemyOffense "100,54|78,68|71,99" \
--ComputerRace Random \
--ComputerDifficulty VeryHard
```

