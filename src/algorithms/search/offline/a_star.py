from math import sqrt

from vs.constants import VS
from core.map import Map
from algorithms.queue.priority_queue import PriorityQueue
from algorithms.queue.priotirized_item import PrioritizedItem
from utils.types import Position, PositionList, Action

class aStar():
    def __init__ (self, map: Map, cost_line = 1.0, cost_diag = 1.5):
        self.map = map             # an instance of the class Map
        self.open: PriorityQueue[float, tuple[Position, PositionList, float]] = None       # the frontier of the search algorithm
        self.cost_line = cost_line # the cost to move one step in the horizontal or vertical
        self.cost_diag = cost_diag # the cost to move one step in any diagonal
        self.tlim = float('inf')    # when the walk time reach this threshold, the plan is aborted
        self.cells = {}
        
        self.incr = {              # the increments for each walk action
            0: (0, -1),             #  u: Up
            1: (1, -1),             # ur: Upper right diagonal
            2: (1, 0),              #  r: Right
            3: (1, 1),              # dr: Down right diagonal
            4: (0, 1),              #  d: Down
            5: (-1, 1),             # dl: Down left left diagonal
            6: (-1, 0),             #  l: Left
            7: (-1, -1)             # ul: Up left diagonal
        }

    # Find possible actions of a given position (state)
    def get_possible_actions(self, pos) -> list[tuple[int, int]]:
        x, y = pos
        actions = []

        if self.map.in_map(pos):
            incr = 0
            for key in self.incr:
                possible_pos = self.map.get_actions_results(pos)
                if possible_pos[incr] == VS.CLEAR:
                    actions.append((self.incr[key][0], self.incr[key][1]))

                incr += 1
            
        return actions

    # Verifies if pos (state) is already in the frontier
    def in_the_frontier(self, pos):
        if(self.open == None):
            return False

        for cell in self.open:
            frontier_pos, _, _ = cell.item
            if pos == frontier_pos:
                return True
            
        return False
    

    def euclidean_distance(self, start: Position, end: Position) -> float:
        return sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)
    
    def sum_positions(self, a: Position, b: Position) -> Position:
        return (a[0] + b[0], a[1] + b[1])
    
    def is_action_in_line(self, action: Action) -> bool:
        return action[0] == 0 or action[1] == 0

    def search(self, start: tuple[int, int], goal: tuple[int, int], tlim=float('inf')) -> tuple[PositionList, float]:
        self.tlim = tlim

        self.open = PriorityQueue([PrioritizedItem(self.euclidean_distance(start, goal), (start, [], 0))])
        closed = set()

        if start == goal:
            return [], 0
        
        while self.open:
            curr_pos, curr_plan, curr_acc_cost = self.open.pop()
            closed.add(curr_pos)

            possible_actions = self.get_possible_actions(curr_pos)

            for action in possible_actions:
                neighbour = self.sum_positions(curr_pos, action)
                
                if self.map.in_map(neighbour) and neighbour not in closed and not self.in_the_frontier(neighbour):
                    difficulty = self.map.get_difficulty(neighbour)
                    new_acc_cost = curr_acc_cost + (self.cost_line if self.is_action_in_line(action) else self.cost_diag) * difficulty
                    new_plan = curr_plan + [action]

                    if neighbour == goal:
                        if new_acc_cost > self.tlim:
                            return [], -1

                        return new_plan, new_acc_cost

                    heuristic = self.euclidean_distance(neighbour, goal)
                    self.open.push(PrioritizedItem(new_acc_cost + heuristic, (neighbour, new_plan, new_acc_cost)))
