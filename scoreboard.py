import turtle as t
import logging

logger = logging.getLogger(__name__)
FONT = ("TIMES NEW ROMAN", 24, "bold")

class Score(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.hideturtle()
        self.color("white")
        self.teleport(-290, 350)
        self.value = 0
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"SCORE: <{self.value:04}>", font=FONT)

    def set(self, value:int) -> None:
        self.value = value if value > 0 else self.value
        self.update()
        
class HighScore(Score):
    def __init__(self) -> None:
        super().__init__()
        self.teleport(-40, 350)
    
    def update(self) -> None:
        self.clear()
        self.write(f"HIGH SCORE: <{self.value:04}>", font=FONT)


class LifeScore(Score):
    def __init__(self) -> None:
        super().__init__()
        self.teleport(-290, -390)
        self.value = 3
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"{'X'*self.value}", font=FONT)
        
class Level(Score):
    def __init__(self) -> None:
        super().__init__()
        self.teleport(135, -390)
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"LEVEL: {self.value:2}", font=FONT)