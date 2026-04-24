import sys
sys.path.insert(1, "python-sc2")

from bot import ICBot, EnemyBot, EnemyBotCycleAttack

import argparse
import asyncio
import logging
import aiohttp
import sc2
from sc2.client import Client
from sc2.player import Bot, Computer
from sc2 import Race, Difficulty
from sc2.protocol import ConnectionAlreadyClosed
import time

import multiprocessing as mp

logging.getLogger("sc2").setLevel(logging.ERROR)
logging.getLogger("sc2.protocol").setLevel(logging.ERROR)
logging.getLogger("sc2.controller").setLevel(logging.ERROR)


# -------------------------
# LADDER MODE
# -------------------------
def run_ladder_game(args, bot):
    host = args.LadderServer if args.LadderServer else "127.0.0.1"

    host_port = args.GamePort
    lan_port = args.StartPort

    ports = [lan_port + p for p in range(1, 6)]

    portconfig = sc2.portconfig.Portconfig()
    portconfig.shared = ports[0]
    portconfig.server = [ports[1], ports[2]]
    portconfig.players = [[ports[3], ports[4]]]

    g = join_ladder_game(
        host=host,
        port=host_port,
        players=[bot],
        realtime=args.Realtime,
        portconfig=portconfig
    )

    result = asyncio.get_event_loop().run_until_complete(g)
    return result


async def join_ladder_game(
    host, port, players, realtime, portconfig,
    save_replay_as=None, step_time_limit=None, game_time_limit=None
):
    ws_url = f"ws://{host}:{port}/sc2api"

    ws_connection = await aiohttp.ClientSession().ws_connect(ws_url, timeout=120)
    client = Client(ws_connection)

    try:
        result = await sc2.main._play_game(
            players,
            client,
            realtime,
            portconfig,
            step_time_limit,
            game_time_limit
        )

    except ConnectionAlreadyClosed:
        logging.error("Connection closed before game ended")
        return None

    finally:
        await ws_connection.close()

    return result


# -------------------------
# ARGUMENTS
# -------------------------
def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--GamePort", type=int)
    parser.add_argument("--StartPort", type=int)
    parser.add_argument("--LadderServer", type=str)

    parser.add_argument("--Sc2Version", type=str)
    parser.add_argument("--Map", type=str, default="Simple64")

    parser.add_argument("--Industry", type=str)
    parser.add_argument("--Offense", type=str)
    parser.add_argument("--Defense", type=str)
    parser.add_argument("--Final", type=str)

    parser.add_argument("--ComputerRace", type=str, default="Terran",
                        help="Computer race. One of [Terran, Zerg, Protoss, Random]. Default is Terran. Only for local play.")
    parser.add_argument("--ComputerDifficulty", type=str, default="VeryHard",
                        help=f"Computer difficulty. One of [VeryEasy, Easy, Medium, MediumHard, Hard, Harder, VeryHard, CheatVision, CheatMoney, CheatInsane]. Default is VeryEasy. Only for local play.")

    parser.add_argument(
        "--EnemyOffense",
        type=str,
        default="25,80|50,80|75,80"
    )

    parser.add_argument("--OpponentId", type=str)
    parser.add_argument("--Realtime", action="store_true")

    args = parser.parse_args()

    if args.OpponentId is None:
        args.OpponentId = "BotOpponent"

    return args


# -------------------------
# BOT LOADERS
# -------------------------
def load_main_bot(args):
    ai = ICBot(args)
    return Bot(Race.Zerg, ai)

def load_enemy_bot(args):
    # ai = EnemyBot(args)
    ai = EnemyBotCycleAttack(args)
    
    return Bot(Race.Terran, ai)


# -------------------------
# RUN ONE MATCH
# -------------------------
def run(game_id, args):
    print(f"Starting Match {game_id + 1}")

    if args.LadderServer:
        bot = load_main_bot(args)
        run_ladder_game(args, bot)

    else:
        print("Loading bot1")
        bot1 = load_main_bot(args)

        print("Loading bot2")
        bot2 = load_enemy_bot(args)

        print("Starting run_game")

        result = sc2.run_game(
            sc2.maps.get(args.Map),
            [
                bot1,
                bot2 
                # Computer(Race[args.ComputerRace], Difficulty[args.ComputerDifficulty])
            ],
            realtime=args.Realtime,
            sc2_version=args.Sc2Version
        )

        print("Match Result:", result)

    print(f"Finished Match {game_id + 1}")


# -------------------------
# START 3 MATCHES SEQUENTIALLY
# -------------------------
# if __name__ == "__main__":
#     args = parse_arguments()
#     mp.set_start_method("spawn", force=True)

#     processes = []
#     for i in range(3):
#         p = mp.Process(target=run, args=(i, args))
#         p.start()
#         processes.append(p)

#     for p in processes:
#         p.join()

###
# STARTING 1 MATCH AT A TIME
###

if __name__ == "__main__":
    args = parse_arguments()

    for i in range(3):
        print("Starting paired match", i+1)
        run(i, args)