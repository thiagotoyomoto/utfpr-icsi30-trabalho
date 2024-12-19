class Stack[T]:
    def __init__(self, items: list[T] = None):
        self._items = items if items is not None else []
        self._length = len(self._items)

    def push(self, item: T):
        self._items.append(item)
        self._length += 1

    def pop(self) -> T:
        if not self._length == 0:
            self._length -= 1
            return self._items.pop()

    def __len__(self) -> int:
        return self._length
    
    def __iter__(self):
        return self._items.__iter__()

    def is_empty(self) -> bool:
        return self._length == 0