from __future__ import annotations
import turtle as t
import logging
from scoreboard import Score, HighScore, LifeScore, Level, GameOverText
from time import sleep, perf_counter
from spaceships import SpaceShip, Invader, Bullet, N, S
from collections import deque
from random import randint
from contextlib import suppress
from fortresses import Fortress
from dataclasses import dataclass, field
from queue import Queue
from collections.abc import Callable
import threading

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_LEFT_LIMIT_OBJECTS = - SCREEN_WIDTH / 2 + 5
SCREEN_RIGHT_LIMIT_OBJECTS = SCREEN_WIDTH / 2 - 15
type numeric = int | float
rlock = threading.RLock()

@dataclass
class ItemsToRemove:
    bullets: set[int] = field(default_factory=set)
    invaders: set[tuple[int, int]] = field(default_factory=set)
    fortresses: set[int] = field(default_factory=set)
    
class StopThreadException(Exception): pass
    
def cyclic_execution(fn: Callable[[], None], app: App) -> None:
    while True:
        fn()
        sleep(0.001)
        if not app.run:
            logger.info("Stop cyclic_execution with ExitException.")
            raise StopThreadException()

def perform_tasks(queue: Queue) -> None:
    if queue.qsize() > 0:
        task = queue.get()
        task()
        queue.task_done()

class App():
    def __init__(self):
        self.screen = t.Screen()
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.title("Turtle invaders")
        self.screen.bgcolor("black")
        self.screen.tracer(0)
        self.screen.listen()
        self.game_score = Score()
        self.game_high_score = HighScore()
        self.game_lifes = LifeScore()
        self.game_level = Level()
        self.game_level_up = False
        self.user = SpaceShip()
        self.invaders = None
        self.invaders_movement_direction = 1 # values -1 or 1
        self.initialize_invaders()
        self.bullets = []
        self.to_remove = ItemsToRemove()
        self.tasks = Queue()
        self.tasks_gui = Queue()
        self.run = True
        self.fortresses = None
        self.cooldown_user_shoot = 0.5
        self.cooldown_user_last_shoot = perf_counter() - 30
        self.cooldown_invaders_shoot = 2
        self.cooldown_invaders_last_shoot = perf_counter() - 30
        self.cooldown_invaders_movement = 2
        self.cooldown_invaders_last_move = perf_counter()
        self.cooldown_bullet_movement = 0.005
        self.cooldown_bullet_last_move = perf_counter() - 30
        self.initialize_fortressesV2(-290)
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()-15) if self.user.xcor() - 15 > SCREEN_LEFT_LIMIT_OBJECTS else ..., "Left")
        self.screen.onkey(lambda: self.user.teleport(self.user.xcor()+15) if self.user.xcor() + 15 < SCREEN_RIGHT_LIMIT_OBJECTS else ..., "Right")
        self.screen.onkey(self.user_shoot, "space")
        self.screen.onkey(self.stop, "q")
    
    ### INITIALIZATION ###
    def initialize_invaders(self, start_y_cor: numeric=300, rows: int=6) -> None:
        START_X = int(SCREEN_WIDTH / 2 - 30)
        END_X = int(SCREEN_WIDTH / 4)
        self.invaders_movement_direction = 1
        self.invaders = [
            [ Invader(x, start_y_cor - i * 40) for i in range(rows) ] for x in range(-START_X, END_X, 40)
        ]
      
    def initialize_fortresses(self, y: numeric, number: int=4) -> None:
        if number < 0:
            raise ValueError(f"Parameter must be greater or equal null. Given: {number}.")
        distance = int(SCREEN_WIDTH / (number + 1))
        self.fortresses = [
            Fortress(x, y) for x in range(int(SCREEN_LEFT_LIMIT_OBJECTS) + distance, int(SCREEN_RIGHT_LIMIT_OBJECTS), distance)
        ]
        
    def initialize_fortressesV2(self, y: numeric, number: int=4) -> list[Fortress]:
        if number < 0:
            raise ValueError(f"Parameter must be greater or equal null. Given: {number}.")
        distance = int(SCREEN_WIDTH / (number + 1))
        self.fortresses = []
        for x in range(int(SCREEN_LEFT_LIMIT_OBJECTS) + distance, int(SCREEN_RIGHT_LIMIT_OBJECTS), distance):
            self.fortresses.append(
                Fortress(x-Fortress.radius, y)
            )
            self.fortresses.append(
                Fortress(x+Fortress.radius, y)
            )

    def reset_bullets(self) -> None:
        if len(self.bullets) > 0:
            logger.debug("Reset list of bullets")
            [
                self.tasks_gui.put(bullet.destroy) for bullet in self.bullets
            ]
            rlock.acquire()
            self.to_remove.bullets.update([i for i in range(len(self.bullets))])
            rlock.release()
      
    ### MOVEMENTS ###
    def move_invaders(self, sideward_step: numeric=15, forward_step: numeric=30) -> None:
        if perf_counter() - self.cooldown_invaders_last_move < self.cooldown_invaders_movement:
            return
        self.cooldown_invaders_last_move = perf_counter()
        direction = self.invaders_movement_direction
        # first_column_to_move = {-1: 0, 1: -1}
        x_is_found = False
        x = None
        for row in self.invaders[::direction*-1]:
            for i in row:
                if i is not None:
                    x = i.xcor()
                    x_is_found = True
                if x_is_found:
                    break
            if x_is_found:
                break
        if x is None: 
            logger.debug("Missing invaders.")
            logger.debug("Asume a level up...")
            self.game_level_up = True
            return
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
        if perf_counter() - self.cooldown_bullet_last_move < self.cooldown_bullet_movement:
            return
        self.cooldown_bullet_last_move = perf_counter()
        [
            bullet.move(1) for bullet in self.bullets
        ]

    ### SHOOTING ###
    def invaders_shoot(self) -> None:
        if perf_counter() - self.cooldown_invaders_last_shoot < self.cooldown_invaders_shoot:
            return
        column = randint(0, len(self.invaders)-1)
        for invader in self.invaders[column][::-1]:
            if invader is not None:
                rlock.acquire()
                self.bullets.append(invader.shoot()) 
                rlock.release()
                self.cooldown_invaders_last_shoot = perf_counter()
                return
            
    def user_shoot(self, time_interval: numeric=0.5) -> None:
        if perf_counter() - self.cooldown_user_last_shoot > time_interval:
            rlock.acquire()
            self.bullets.append(self.user.shoot())
            rlock.release()
            self.cooldown_user_last_shoot = perf_counter()

    ### CHECKS ###
    def check_collisions(self) -> None:
        for i, bullet in enumerate(self.bullets):
            if i in self.to_remove.bullets:
                continue
            if (
                (self.user.xcor() - bullet.xcor())**2 + (self.user.ycor() - bullet.ycor())**2 <= (self.user.radius + bullet.radius)**2 and
                self.user.heading() != bullet.heading()
            ):
                logger.debug("Bullet hit user (%s, %s)", bullet.xcor(), bullet.ycor())
                self.to_remove.bullets.add(i)
                self.tasks_gui.put(self.game_lifes.reduce_)
                self.tasks_gui.put(self.game_lifes.update)
                self.tasks.put(self.reset_bullets)
                self.tasks.put(self.check_lifes)
            for fortress in self.fortresses:
                if (
                    (fortress.xcor() - bullet.xcor())**2 + (fortress.ycor() - bullet.ycor())**2 <= (fortress.radius + bullet.radius)**2
                ):
                    logger.debug("Bullet hit fortress (%s, %s)", bullet.xcor(), bullet.ycor())
                    self.tasks.put(fortress.hit)
                    self.tasks_gui.put(fortress.change_color)
                    self.tasks_gui.put(bullet.destroy)
                    self.to_remove.bullets.add(i)
            for col, rows in enumerate(self.invaders):
                for row, invader in enumerate(rows):
                    if (
                        invader is not None and
                        (invader.xcor() - bullet.xcor())**2 + (invader.ycor() - bullet.ycor())**2 <= (invader.radius + bullet.radius)**2 and
                        invader.heading() != bullet.heading()
                    ):
                        logger.debug("Bullet hit invader (%s, %s)", bullet.xcor(), bullet.ycor())
                        self.tasks_gui.put(invader.destroy)
                        self.tasks_gui.put(bullet.destroy)
                        self.to_remove.bullets.add(i)
                        self.tasks.put((lambda: self.game_score.increase(1)))
                        self.tasks_gui.put(self.game_score.update)
                        self.to_remove.invaders.add((col, row))
                    
    def check_lifes(self,) -> None:
        if self.game_lifes.value <= 0:
            logger.info("User lost all life points")
            self.tasks_gui.put(self.game_over)
            self.stop()
            
    def check_invaders_win(self) -> bool:
        for column in self.invaders:
            for row in column:
                if row is not None:
                    if row.ycor() <= -280:
                        return True
        return False
    
    ### UPDATE GAME STATE ###
    def increase_game_speed(self) -> None:
        self.cooldown_bullet_movement -= 0.001
        self.cooldown_invaders_movement -= 0.03
        self.cooldown_user_shoot -= 0.009
    
    def increase_level(self) -> None:
        if self.game_level_up:
            self.game_level_up = False
            logger.debug("Updating level")
            self.tasks.put(self.reset_bullets)
            self.tasks.put((lambda: self.game_level.increase(1)))
            self.tasks_gui.put(self.initialize_invaders)
            self.tasks_gui.put(self.game_level.update)
            self.tasks.put(self.increase_game_speed)
            logger.debug("Updated level")
            
    def game_over(self) -> None:
        logger.info("Game over.")
        GameOverText()
        self.screen.update()
        self.screen.exitonclick()

    def remove_items(self) -> None:
        for item in ("fortresses", "bullets", "invaders"):
            if item in ("invaders",):
                lst = [
                    [
                        item for row, item in enumerate(rows) if (column, row) not in self.to_remove.invaders
                    ] for column, rows in enumerate(self.invaders) 
                ]
            else:
                lst = [ obj for i, obj in enumerate(getattr(self, item)) if i not in getattr(self.to_remove, item)]
            rlock.acquire()
            setattr(self, item, lst)
            rlock.release()
            rlock.acquire()
            getattr(self.to_remove, item).clear()
            rlock.release()
        
    def stop(self) -> None:
        logger.info("Stopping game...")
        self.run = False
        
def main():
    logger.info("Starting game...")
    app = App()
    logger.info("Starting game... is done.")
    with suppress(FileNotFoundError):
        logger.debug("Searching for stored high score")
        with open("highscore") as f:
            logger.debug("Reading high score")
            app.game_high_score.value = int(f.read())
            app.game_high_score.update()
            logger.debug("Set high score")
        logger.debug("Searching for stored high score is done.")
            
    logger.info("Starting thread with tasks...")
    th = threading.Thread(target=(lambda: cyclic_execution(lambda: perform_tasks(app.tasks), app)), name="tasks")
    th.start()
    logger.info("Start main thread...")
    while app.run:
        app.invaders_shoot()
        app.move_invaders()
        app.move_bullets()
        app.check_collisions()
        app.tasks.put(app.remove_items)
        app.increase_level()
        if app.check_invaders_win():
            app.stop()
            app.game_over()
        perform_tasks(app.tasks_gui)
        app.screen.update()
        sleep(0.001)
    logger.info("Main thread is stopping...")
    logger.debug("Tasks thread is still alive? %s", th.is_alive())
    logger.info("Saving high score...")
    if app.game_score.value > app.game_high_score.value:
        logger.debug("Score is higher then current high score.")
        with open("highscore", "w") as f:
            f.write(str(app.game_score.value))
            logger.debug("New high score is stored")
    logger.info("Saving high score... is done.")
    
if __name__ == "__main__":
    main()
