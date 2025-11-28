import turtle as t

class Fortress(t.Turtle):
    def __init__(self, x: int | float, y: int | float):
        super().__init__()
        self.penup()
        self.color("green")
        self.teleport(x, y)
        self.shape("square")
        self.lifes = 10
        
    def hit(self) -> None:
        self.lifes -= 1
        if self.lifes <= 0:
            self.hideturtle()