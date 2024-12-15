import sys
import os
import time

from vs.environment import Env
from agents.explorer import Explorer
from agents.rescuer import Rescuer
from pathlib import Path
from vs.constants import VS

def create_explorers(count, env, explorer_file, rescuer, dirs):
    explorers = []
    for i in range(0, count):
        explorers.append(Explorer(env, explorer_file, rescuer, dirs[i]))
    return explorers

def main(data_folder_name, cfg_ag_folder):
    TOTAL_EXPLORERS = 4
    EXPLORERS_DIRS = [
        [VS.DIR_NORTH, VS.DIR_NORTHEAST, VS.DIR_EAST, VS.DIR_SOUTHEAST, VS.DIR_SOUTH, VS.DIR_SOUTHWEST, VS.DIR_WEST, VS.DIR_NORTHWEST],
        [VS.DIR_EAST, VS.DIR_SOUTHEAST, VS.DIR_SOUTH, VS.DIR_SOUTHWEST, VS.DIR_WEST, VS.DIR_NORTHWEST, VS.DIR_NORTH, VS.DIR_NORTHEAST],
        [VS.DIR_SOUTH, VS.DIR_SOUTHWEST, VS.DIR_WEST, VS.DIR_NORTHWEST, VS.DIR_NORTH, VS.DIR_NORTHEAST, VS.DIR_EAST, VS.DIR_SOUTHEAST],
        [VS.DIR_WEST, VS.DIR_NORTHWEST, VS.DIR_NORTH, VS.DIR_NORTHEAST, VS.DIR_EAST, VS.DIR_SOUTHEAST, VS.DIR_SOUTH, VS.DIR_SOUTHWEST]
    ]

    env = Env(data_folder_name)
    explorer_file = os.path.join(cfg_ag_folder, "explorer_config.txt")
    rescuer_file = os.path.join(cfg_ag_folder, "rescuer_config.txt")
    
    rescuer = Rescuer(env, rescuer_file, TOTAL_EXPLORERS)
    explorers = create_explorers(TOTAL_EXPLORERS, env, explorer_file, rescuer, EXPLORERS_DIRS)

    env.run()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
        cfg_ag_folder = sys.argv[2]
    else:
        cur_folder = Path.cwd()
        data_folder = os.path.join(cur_folder, "datasets", "data_300v_90x90")
        cfg_ag_folder = os.path.join(cur_folder, "config")
        
    main(data_folder, cfg_ag_folder)
