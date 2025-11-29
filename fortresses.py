import turtle as t
from itertools import cycle

type numeric = int | float

COLORS = cycle(("blue", "white", "yellow", "red", "green"))

class Fortress(t.Turtle):
    def __init__(self, x: numeric, y: numeric):
        super().__init__()
        self.penup()
        self.color("green")
        self.teleport(x, y)
        self.shape("square")
        self.lifes = 10
        self.radius = 10
        
    def hit(self) -> None:
        self.lifes -= 1
        self.color(next(COLORS))
        
    def destroy(self) -> None:
        self.hideturtle() 