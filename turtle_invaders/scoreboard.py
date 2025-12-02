import turtle as t
import logging

logger = logging.getLogger(__name__)
NORMAL_FONT = ("TIMES NEW ROMAN", 24, "bold")
BIG_FONT = ("TIMES NEW ROMAN", 50, "bold")
HUGE_FONT = ("TIMES NEW ROMAN", 60, "bold")


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
        self.write(f"SCORE: <{self.value:04}>", font=NORMAL_FONT)

    def increase(self, value: int) -> None:
        self.value += value
        
class HighScore(t.Turtle):
    def __init__(self, value: int=0) -> None:
        super().__init__()
        self.penup()
        self.hideturtle()
        self.color("white")
        self.teleport(-40, 350)
        self.value = value
        self.update()
    
    def update(self) -> None:
        self.clear()
        self.write(f"HIGH SCORE: <{self.value:04}>", font=NORMAL_FONT)


class LifeScore(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.hideturtle()
        self.color("white")
        self.teleport(-290, -390)
        self.value = 3
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"{'X'*self.value}", font=NORMAL_FONT)
        
    def reduce_(self,) -> None:
        self.value -= 1
        
class Level(t.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.penup()
        self.hideturtle()
        self.color("white")
        self.teleport(135, -390)
        self.value = 0
        self.update()
        
    def update(self) -> None:
        self.clear()
        self.write(f"LEVEL: {self.value:2}", font=NORMAL_FONT)

    def increase(self, value: int) -> None:
        self.value += value
        
class GameOverLabel(t.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("red")
        self.teleport(-200, 0)
        self.write("GAME OVER", font=BIG_FONT)
        
class CountDownLabel(t.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("white")
        self.teleport(-30, 0)
        
    def update(self, value: int | str) -> None:
        self.clear()
        self.write(f"{value}", font=HUGE_FONT)
        
    def hide(self) -> None:
        self.clear()
        