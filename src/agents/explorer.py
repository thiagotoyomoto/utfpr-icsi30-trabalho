# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the explorer goes back to the base.

from vs.abstract_agent import AbstAgent
from vs.constants import VS
from vs.environment import Env
from core.map import Map
from algorithms.stack import Stack
from utils.types import Position
import random

def subtract_position(a: Position, b: Position) -> Position:
    return (a[0] - b[0], a[1] - b[1])

def add_position(a: Position, b: Position) -> Position:
    return (a[0] + b[0], a[1] + b[1])

def invert_position(a: Position) -> Position:
    return (-a[0], -a[1])

class Explorer(AbstAgent):
    """class attribute"""

    MAX_DIFFICULTY = 1  # the maximum degree of difficulty to enter into a cell

    def __init__(self, env: Env, config_file: str, resc, dirs: list[int]):
        """Construtor do agente random on-line
        @param env: a reference to the environment
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.walk_time = (
            0  # time consumed to walk when exploring (to decide when to come back)
        )
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc  # reference to the rescuer agent
        self.x = 0  # current x position relative to the origin 0
        self.y = 0  # current y position relative to the origin 0
        self.map = Map()  # create a map for representing the environment
        self.victims = {}  # a dictionary of found victims: (seq): ((x,y), [<vs>])
        # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

        self.directions = dirs

        self.untried: dict[Position, list[bool]] = {}
        self.unbacktracked: dict[Position, Stack[Position]] = {}
        
        self.last_dir_incr: Position = None

    def get_next_position(self):
        neighbourhood = self.check_walls_and_lim()
        curr_pos = (self.x, self.y)

        if curr_pos not in self.untried:
            self.untried[curr_pos] = [True] * 8

            for direction in self.directions:
                if neighbourhood[direction] != VS.CLEAR:
                    self.untried[curr_pos][direction] = False
        
        if curr_pos not in self.unbacktracked:
            self.unbacktracked[curr_pos] = Stack()

        if self.last_dir_incr != None:
            self.unbacktracked[curr_pos].push(self.last_dir_incr)
            
        filtered_untried = list(filter(lambda item: item[1], enumerate(self.untried[curr_pos])))
        if filtered_untried:
            direction = random.choice(filtered_untried)[0]
            self.untried[curr_pos][direction] = False

            self.last_dir_incr = Explorer.AC_INCR[direction]
            
            return Explorer.AC_INCR[direction]

        self.last_dir_incr = None
        return invert_position(self.unbacktracked[curr_pos].pop())

    def explore(self):
        # get an random increment for x and y
        dx, dy = self.get_next_position()

        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        # Test the result of the walk action
        # Should never bump, but for safe functionning let's test
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add(
                (self.x + dx, self.y + dy),
                VS.OBST_WALL,
                VS.NO_VICTIM,
                self.check_walls_and_lim(),
            )
            # print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy

            rtime_diff = rtime_bef - rtime_aft

            # update the walk time
            self.walk_time += rtime_diff
            # print(f"{self.NAME} walk time: {self.walk_time}")

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                # print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                # print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")

            # Calculates the difficulty of the visited cell
            difficulty = rtime_diff / self.COST_LINE if dx == 0 or dy == 0 else self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            # print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    def come_back(self):
        print("Calling come_back")

        dx, dy = self.walk_stack.pop()
        dx = dx * -1
        dy = dy * -1

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(
                f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}"
            )
            return

        if result == VS.EXECUTED:
            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            # print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")

    def deliberate(self) -> bool:
        """The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # forth and back: go, read the vital signals and come back to the position

        time_tolerance = 2 * self.COST_DIAG * Explorer.MAX_DIFFICULTY + self.COST_READ

        # keeps exploring while there is enough time
        if self.walk_time < (self.get_rtime() - time_tolerance):
            self.explore()
            return True

        # no more come back walk actions to execute or already at base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False

        # proceed to the base
        self.come_back()
        return True
