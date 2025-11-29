import turtle as t
import logging
from scoreboard import Score, HighScore, LifeScore, Level, GameOverText
from time import sleep, perf_counter
from spaceships import SpaceShip, Invader, Bullet, N, S
from collections import deque
from random import randint
from contextlib import suppress
from fortresses import Fortress

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_LEFT_LIMIT_OBJECTS = - SCREEN_WIDTH / 2 + 5
SCREEN_RIGHT_LIMIT_OBJECTS = SCREEN_WIDTH / 2 - 15
type numeric = int | float

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
        self.user_last_shoot = perf_counter() - 30
        self.user_is_hit = False
        self.invaders = self.initialize_invaders()
        self.invaders_movement_direction = 1 # values -1 or 1
        self.invaders_last_shoot = perf_counter() - 30
        self.invaders_last_move = perf_counter()
        self.bullets = []
        self.run = True
        self.fortresses = self.initialize_fortressesV2(-290)
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()-15) if self.user.xcor() - 15 > SCREEN_LEFT_LIMIT_OBJECTS else ..., "Left")
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()+15) if self.user.xcor() + 15 < SCREEN_RIGHT_LIMIT_OBJECTS else ..., "Right")
        self.screen.onkey(self.user_shoot, "space")
        self.screen.onkey(self.stop, "q")
    
    ### INITIALIZATION ###
    def initialize_invaders(self, start_y_cor: numeric=300, rows: int=6) -> list[list[Invader]]:
        START_X = int(SCREEN_WIDTH / 2 - 30)
        END_X = int(SCREEN_WIDTH / 4)
        return [
            [ Invader(x, start_y_cor - i * 40) for i in range(rows) ] for x in range(-START_X, END_X, 40)
        ]
      
    def initialize_fortresses(self, y: numeric, number: int=4) -> list[Fortress]:
        if number < 0:
            raise ValueError(f"Parameter must be greater or equal null. Given: {number}.")
        distance = int(SCREEN_WIDTH / (number + 1))
        return [
            Fortress(x, y) for x in range(int(SCREEN_LEFT_LIMIT_OBJECTS) + distance, int(SCREEN_RIGHT_LIMIT_OBJECTS), distance)
        ]
        
    def initialize_fortressesV2(self, y: numeric, number: int=4) -> list[Fortress]:
        if number < 0:
            raise ValueError(f"Parameter must be greater or equal null. Given: {number}.")
        distance = int(SCREEN_WIDTH / (number + 1))
        result = []
        for x in range(int(SCREEN_LEFT_LIMIT_OBJECTS) + distance, int(SCREEN_RIGHT_LIMIT_OBJECTS), distance):
            result.append(
                Fortress(x-Fortress.radius, y)
            )
            result.append(
                Fortress(x+Fortress.radius, y)
            )
        return result
      
    def move_invaders(self, sideward_step: numeric=15, forward_step: numeric=30) -> None:
        if perf_counter() - self.invaders_last_move < 1:
            return
        self.invaders_last_move = perf_counter()
        direction = self.invaders_movement_direction
        first_column_to_move = {-1: 0, 1: -1}
        for i in self.invaders[first_column_to_move[direction]]:
            if i is not None:
                x = i.xcor()
                break
        if SCREEN_LEFT_LIMIT_OBJECTS < x + sideward_step*direction < SCREEN_RIGHT_LIMIT_OBJECTS:
            [
                [item.teleport(item.xcor()+sideward_step*direction, item.ycor()) for item in column if item is not None] for column in self.invaders
            ]
        else:
            self.invaders_movement_direction *= -1
            [
                [item.teleport(item.xcor(), item.ycor()-forward_step) for item in column if item is not None] for column in self.invaders
            ]
            
    def move_bullets(self) -> None:
        [
            bullet.move(1) for bullet in self.bullets
        ]

    def invaders_shoot(self, time_interval: int=2) -> None:
        if perf_counter() - self.invaders_last_shoot > time_interval:
            column = randint(0, len(self.invaders)-1)
            for invader in self.invaders[column][::-1]:
                if invader is not None:
                    self.bullets.append(invader.shoot()) 
                    self.invaders_last_shoot = perf_counter()
                    return
                
    def user_shoot(self, time_interval: numeric=0.5) -> None:
        if perf_counter() - self.user_last_shoot > time_interval:
            self.bullets.append(self.user.shoot())
            self.user_last_shoot = perf_counter()

        
    def check_collisions(self) -> None:
        bullets_to_remove = deque()
        for column, rows in enumerate(self.invaders):
            for row, invader in enumerate(rows):
                for i, bullet in enumerate(self.bullets):
                    if (
                        invader is not None and
                        (invader.xcor() - bullet.xcor())**2 + (invader.ycor() - bullet.ycor())**2 <= (invader.radius + bullet.radius)**2 and
                        invader.heading() != bullet.heading()
                    ):
                        logger.debug("Bullet hit invader (%s, %s)", bullet.xcor(), bullet.ycor())
                        invader.damage()
                        bullet.damage()
                        bullets_to_remove.append(i)
                        self.invaders[column][row] = None
                        self.score.increase(1)
                    if (
                        (self.user.xcor() - bullet.xcor())**2 + (self.user.ycor() - bullet.ycor())**2 <= (self.user.radius + bullet.radius)**2 and
                        self.user.heading() != bullet.heading()
                    ):
                        logger.debug("Bullet hit user (%s, %s)", bullet.xcor(), bullet.ycor())
                        bullets_to_remove.append(i)
                        self.lifes.reduce_()
                        self.user_is_hit = True
                        return
        for i, bullet in enumerate(self.bullets):
            for k, fortress in enumerate(self.fortresses):
                if (
                        (fortress.xcor() - bullet.xcor())**2 + (fortress.ycor() - bullet.ycor())**2 <= (fortress.radius + bullet.radius)**2
                ):
                    logger.debug("Bullet hit fortress (%s, %s)", bullet.xcor(), bullet.ycor())
                    fortress.hit()
                    bullet.damage()
                    bullets_to_remove.append(i)
        bullets = [ bullet for i, bullet in enumerate(self.bullets) if i not in bullets_to_remove ]
        self.bullets = bullets
        
                    
    def clear_invader_columns(self):
        columns_to_remove = deque()
        [
            columns_to_remove.append(column) for column, rows in enumerate(self.invaders) if not any(rows)
        ]
        [
            self.invaders.pop(i) for i in columns_to_remove
        ]
        
        
    def check_lifes(self,) -> None:
        if self.lifes.value <= 0:
            self.run = False
            self.game_over()
            
    def check_fortresses(self) -> None:
        to_destroy = deque()
        for i, fortress in enumerate(self.fortresses):
            if fortress.lifes <= 0:
                fortress.destroy()
                to_destroy.append(i)
        [
            self.fortresses.pop(i) for i in to_destroy
        ]
        
    def check_invaders_win(self) -> bool:
        for column in self.invaders:
            for row in column:
                if row is not None:
                    if row.ycor() <= -280:
                        return True
        return False
    
    def update_level(self) -> None:
        if len(self.invaders) == 0:
            self.reset_bullets()
            self.invaders = self.initialize_invaders()
            self.level.value += 1
            self.level.update()
            logger.debug("Updated level")
            
    def reset_bullets(self) -> None:
        if len(self.bullets) > 0:
            logger.debug("Reset list of bullets")
            [
                bullet.damage() for bullet in self.bullets
            ]
            self.bullets = []

    def stop(self) -> None:
        self.run = False
        
    def game_over(self) -> None:
        GameOverText()
        self.screen.update()
        sleep(7)
        
def main():
    app = App()
    with suppress(FileNotFoundError):
        logger.debug("Searching for stored high score")
        with open("highscore") as f:
            logger.debug("Reading high score")
            app.high_score.value = int(f.read())
            app.high_score.update()
            logger.debug("Set high score")
    while app.run:
        try:
            app.invaders_shoot()
            app.move_invaders()
            app.move_bullets()
            app.check_collisions()
            if app.user_is_hit:
                app.reset_bullets()
                app.user_is_hit = False
            app.clear_invader_columns()
            app.check_lifes()
            app.check_fortresses()
            app.update_level()
            if app.check_invaders_win():
                app.stop()
                app.check_invaders_win()
                app.game_over()
            app.screen.update()
            sleep(0.001)
        except KeyboardInterrupt:
            app.stop()

    if app.score.value > app.high_score.value:
        logger.debug("Score is higher then current high score.")
        with open("highscore", "w") as f:
            f.write(str(app.score.value))
            logger.debug("New high score is stored")
    
if __name__ == "__main__":
    main()
