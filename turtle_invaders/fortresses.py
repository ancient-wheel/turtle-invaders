import turtle as t
from constants import COLORS
from types_ import numeric


class Fortress(t.Turtle):
    radius = 10

    def __init__(self, x: numeric, y: numeric):
        super().__init__()
        self.penup()
        self.color("green")
        self.teleport(x, y)
        self.shape("square")
        self.lifes = 10

    def hit(self) -> None:
        self.lifes -= 1

    def change_color(self) -> None:
        self.color(next(COLORS))

    def destroy(self) -> None:
        self.hideturtle()
