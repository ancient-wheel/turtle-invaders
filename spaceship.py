import turtle as t

class SpaceShip(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.shape("turtle")
        self.left(90)
        self.color("green")
        self.teleport(0, -330)
        