from __future__ import annotations
import turtle as t
from enum import IntEnum

type numeric = int | float

class ObjectDirection(IntEnum):
    NORTH = 90
    SOUTH = 270

class SpaceShip(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.shape("turtle")
        self.left(ObjectDirection.NORTH.value)
        self.color("green")
        self.teleport(0, -330)
        self.radius = 10
        
    def shoot(self) -> Bullet:
        return Bullet(self.xcor(), self.ycor(), ObjectDirection.NORTH, "green")
    
class Invader(t.Turtle):
    def __init__(self, x: numeric, y: numeric) -> None:
        super().__init__()
        self.penup()
        self.shape("turtle")
        self.left(ObjectDirection.SOUTH.value)
        self.color("blue")
        self.teleport(x, y)
        self.radius = 10
    
    def shoot(self) -> Bullet:
        return Bullet(self.xcor(), self.ycor(), ObjectDirection.SOUTH, self.color()[0])

    def destroy(self) -> None:
        self.hideturtle()
        
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