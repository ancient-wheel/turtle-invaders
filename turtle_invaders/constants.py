from enum import IntEnum


class ObjectDirection(IntEnum):
    NORTH = 90
    SOUTH = 270
    
class Screen(IntEnum):
    WIDTH = 600
    HEIGHT = 800
    LEFT_LIMIT_FOR_OBJECTS = int(-WIDTH/2 + 5)
    RIGHT_LIMIT_FOR_OBJECTS = int(WIDTH/2 - 15)
    
    