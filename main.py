import turtle as t
import logging
from scoreboard import Score, HighScore, LifeScore, Level
from time import sleep
from spaceships import SpaceShip, Invader, Bullet, N, S
from collections import deque

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

class App():
    def __init__(self):
        self.screen = t.Screen()
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.title("Turtle invaders")
        self.screen.bgcolor("black")
        self.screen.tracer(0)
        self.screen.listen()
        self.score = Score()
        self.high_score = HighScore()
        self.lifes = LifeScore()
        self.level = Level()
        self.user = SpaceShip()
        self.invaders = self.initialize_invadors()
        self.invaders_movement_direction = 1 # values -1 or 1
        self.bullets = deque()
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()-10), "Left")
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()+10), "Right")
        self.screen.onkey(lambda: self.bullets.append(self.user.shoot()), "space")
        
    def initialize_invadors(self) -> list[list[Invader]]:
        START_Y = 80
        return [
            [ Invader(x, START_Y+i*40) for i in range(7) ] for x in range(-270, 150, 25)
        ]
        
    def move_invaders(self, sideward_step: int|float=15, forward_step: int|float=10) -> None:
        direction = self.invaders_movement_direction
        most_right_position = SCREEN_WIDTH/2 - 15
        most_left_position = - SCREEN_WIDTH/2 + 5
        first_column_to_move = {-1: 0, 1: -1}
        items = self.invaders[first_column_to_move[direction]]
        for i in items:
            if isinstance(i, Invader):
                x = i.xcor()
                break
        if most_left_position < x + sideward_step*direction < most_right_position:
            [
                [item.teleport(item.xcor()+sideward_step*direction, item.ycor()) for item in column ] for column in self.invaders
            ]
        else:
            self.invaders_movement_direction *= -1
            [
                [item.teleport(item.xcor(), item.ycor()-forward_step) for item in column] for column in self.invaders
            ]
            
    # def invaders_shoot(self) -> None:
        
        
def main():
    try:
        app = App()
        
        while True:
            app.score.increase(1)
            
            # [
            #     bullet.move(15) for bullet in app.bullets
            # ]
            app.move_invaders()
            app.screen.update()
            sleep(0.5)
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    main()
