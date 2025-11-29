from __future__ import annotations
import turtle as t

type numeric = int | float

class SpaceShip(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.shape("turtle")
        self.left(90)
        self.color("green")
        self.teleport(0, -330)
        self.radius = 5
        
    def shoot(self) -> Bullet:
        return Bullet(self.xcor(), self.ycor(), N, "green")
    
class Invader(t.Turtle):
    def __init__(self, x: numeric, y: numeric) -> None:
        super().__init__()
        self.penup()
        self.shape("turtle")
        self.right(90)
        self.color("blue")
        self.teleport(x, y)
        self.radius = 5
    
    def shoot(self) -> Bullet:
        return Bullet(self.xcor(), self.ycor(), S, self.color()[0])

    def damage(self) -> None:
        self.hideturtle()
        
N = 90
S = 270
class Bullet(t.Turtle):
    def __init__(self, x: numeric, y: numeric, direction: int, color: str) -> None:
        super().__init__()
        self.penup()
        self.left(direction)
        self.color(color)
        self.teleport(x, y)
        self.radius = 2
        
    def move(self, step: numeric):
        self.forward(step)
        
    def damage(self) -> None:
        self.hideturtle()