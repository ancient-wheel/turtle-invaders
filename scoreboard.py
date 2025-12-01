import turtle as t
import logging
from time import sleep

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

    def increase(self, value: int) -> None:
        self.value += value
        
class HighScore(Score):
    def __init__(self, value: int=0) -> None:
        super().__init__()
        self.value = value
        self.teleport(-40, 350)
        self.update()
    
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
        
    def reduce_(self,) -> None:
        self.value -= 1
        
class Level(Score):
    def __init__(self) -> None:
        super().__init__()
        self.teleport(135, -390)
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"LEVEL: {self.value:2}", font=FONT)

class GameOverText(t.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("red")
        self.teleport(-200, 0)
        self.write("GAME OVER", font=("Time New Roman", 50, "bold"))
        
class CountDownText(t.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("white")
        self.teleport(-30, 0)
        
    def write_(self, value: int | float | str) -> None:
        self.clear()
        self.write(f"{value}", font=("Time New Roman", 60, "bold"))
        
    def hide(self) -> None:
        self.clear()
        