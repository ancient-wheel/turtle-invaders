import turtle as t

type numeric = int | float

class Fortress(t.Turtle):
    def __init__(self, x: numeric, y: numeric):
        super().__init__()
        self.penup()
        self.color("green")
        self.teleport(x, y)
        self.shape("square")
        self.lifes = 10
        self.radius = 5
        
    def hit(self) -> None:
        self.lifes -= 1
        
    def destroy(self) -> None:
        self.hideturtle() 