from types_ import numeric
from constants import ObjectDirection
import turtle as t

class Bullet(t.Turtle):
    def __init__(self, x: numeric, y: numeric, direction: ObjectDirection, color: str) -> None:
        super().__init__()
        self.penup()
        self.left(direction.value)
        self.color(color)
        self.teleport(x, y)
        self.radius = 3
        
    def move(self, step: numeric):
        self.forward(step)
        
    def destroy(self) -> None:
        self.hideturtle()