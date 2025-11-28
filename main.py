import turtle as t
import logging
from scoreboard import Score, HighScore, LifeScore, Level
from time import sleep, perf_counter
from spaceships import SpaceShip, Invader, Bullet, N, S
from collections import deque
from random import randint

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
        self.invaders_last_shoot = perf_counter() - 30
        self.invaders_last_move = perf_counter()
        self.bullets = []
        self.run = True
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()-10), "Left")
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()+10), "Right")
        self.screen.onkey(lambda: self.bullets.append(self.user.shoot()), "space")
        self.screen.onkey(self.stop, "q")
        
    def initialize_invadors(self) -> list[list[Invader]]:
        START_Y = 80
        return [
            [ Invader(x, START_Y+i*40) for i in range(7) ] for x in range(-270, 150, 25)
        ]
        
    def move_invaders(self, sideward_step: int|float=10, forward_step: int|float=10) -> None:
        if perf_counter() - self.invaders_last_move < 2:
            return
        else:
            self.invaders_last_move = perf_counter()
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
                [item.teleport(item.xcor()+sideward_step*direction, item.ycor()) for item in column if item is not None] for column in self.invaders
            ]
        else:
            self.invaders_movement_direction *= -1
            [
                [item.teleport(item.xcor(), item.ycor()-forward_step) for item in column if item is not None] for column in self.invaders
            ]
            
    def invaders_shoot(self) -> None:
        if perf_counter() - self.invaders_last_shoot > 3:
            column = randint(0, len(self.invaders)-1)
            for invader in self.invaders[column][::-1]:
                if isinstance(invader, Invader):
                    self.bullets.append(invader.shoot()) 
                    self.invaders_last_shoot = perf_counter()
                    return
    
    def move_bullets(self) -> None:
        [
            bullet.move(1) for bullet in self.bullets
        ]
        
    def check_collision(self) -> None:
        # collision with invaders
        for column, rows in enumerate(self.invaders):
            for row, invader in enumerate(rows):
                for i, bullet in enumerate(self.bullets):
                    if (
                        invader is not None and
                        (invader.xcor() - bullet.xcor())**2 +(invader.ycor() - bullet.ycor())**2 <= (invader.radius + bullet.radius)**2 and
                        invader.heading() != bullet.heading()
                    ):
                        logger.debug("Bullet hit invader (%s, %s)", bullet.xcor(), bullet.ycor())
                        invader.damage()
                        bullet.damage()
                        self.bullets.pop(i)
                        self.invaders[column][row] = None
                        self.score.increase(1)
        # collision with user  
        for i, bullet in enumerate(self.bullets):
            if (
                (self.user.xcor() - bullet.xcor())**2 +(self.user.ycor() - bullet.ycor())**2 <= (self.user.radius + bullet.radius)**2 and
                self.user.heading() != bullet.heading()
            ):
                logger.debug("Bullet hit user (%s, %s)", bullet.xcor(), bullet.ycor())
                bullet.damage()
                self.bullets.pop(i)
                self.lifes.reduce_()
        
    def clear_invader_rows(self):
        columns_to_remove = deque()
        for column, rows in enumerate(self.invaders):
            if not any(rows):
                columns_to_remove.append(column)
        [
            self.invaders.pop(i) for i in columns_to_remove
        ]
        
    def stop(self,) -> None:
        self.run = False
        
    def check_lifes(self,) -> None:
        if self.lifes.value <= 0:
            self.run = False
        
        
def main():
    try:
        app = App()
        while app.run:
            app.high_score.increase(1)
            app.move_invaders()
            app.invaders_shoot()
            app.move_bullets()
            app.check_collision()
            app.clear_invader_rows()
            app.check_lifes()
            app.screen.update()
            sleep(0.001)
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    main()
