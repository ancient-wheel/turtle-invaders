from enum import IntEnum
from itertools import cycle

COLORS = cycle(("blue", "white", "yellow", "red", "green"))


class ObjectDirection(IntEnum):
    NORTH = 90
    SOUTH = 270


class Screen(IntEnum):
    WIDTH = 600
    HEIGHT = 800
    LEFT_LIMIT_FOR_OBJECTS = int(-WIDTH / 2 + 5)
    RIGHT_LIMIT_FOR_OBJECTS = int(WIDTH / 2 - 15)
