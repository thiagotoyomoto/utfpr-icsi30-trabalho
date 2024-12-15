from algorithms.queue.priotirized_item import PrioritizedItem
import heapq

class PriorityQueue[P, T]:
    def __init__(self, items: list[PrioritizedItem[P, T]] = []):
        self._items = items

    def push(self, value: PrioritizedItem[P, T]):
        heapq.heappush(self._items, value)

    def pop(self) -> T:
        return heapq.heappop(self._items).item
    
    def __iter__(self):
        return self._items.__iter__()
