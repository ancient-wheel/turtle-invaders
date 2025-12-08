from __future__ import annotations
from contextlib import suppress
import datetime
import json
import turtle as t
import logging
from time import sleep, perf_counter
from random import randint
from dataclasses import dataclass, field
from queue import Queue
from collections.abc import Callable
import threading
from pathlib import Path
from spaceships import SpaceShip, Invader
from scoreboard import Score, HighScore, LifeScore, Level, GameOverLabel
from fortresses import Fortress
from types_ import numeric
from constants import Screen, InvadersMovementDirection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
rlock = threading.RLock()


def run_in_loop(fn: Callable[[], None], app: App) -> None:
    """Call a function in a loop as long as attribute App.run is True
    Used to run a addition thread.

    Keyword arguments:
    argument -- description
        fn (Callable): function
        app (App): application
    Return:
        None
    """
    while app.run:
        fn()
        sleep(0.001)
    logger.info("Stop cyclic_execution with ExitException.")


def perform_task_from(queue: Queue) -> None:
    """Get a single task from a queue and call it.

    Keyword arguments:
    argument -- description
        queue (Queue): queue to get task
    Return: return_description
        None
    """
    if queue.qsize() > 0:
        task = queue.get()
        task()
        queue.task_done()


def read_json(path: str | Path) -> dict[str, int]:
    """Read a json file.

    Keyword arguments:
    argument -- description
        path (str | Path): path to the file
    Return: return_description
        dict[str, int]: dictionary with high scores
    """

    file_path = Path(path) if isinstance(path, str) else path
    with suppress(FileNotFoundError):
        with open(file_path, "r") as f:
            results = json.load(f)
    return results if "results" in locals() else {}


def write_json(dict_: dict[str, int], path: str | Path) -> None:
    """Save a dictionary to a file.

    Keyword arguments:
    argument -- description
        path (str): path to the file
        results (dict[str, int]): existing high scores
    Return: return_description
        None
    """

    file_path = Path(path) if isinstance(path, str) else path
    if file_path.suffix != ".json":
        file_path = file_path.with_suffix(".json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(dict_, f, indent=4)
        logger.debug("New high score is stored")


def add_score(high_score_dict: dict[str, int], score: int) -> dict[str, int]:
    """Add score to a high score list. List contains best ten results.

    Keyword arguments:
    argument -- description
        high_score_dict (dict[str, int]): existing high scores
        score (int): new score to add
    Return: return_description
        dict[str, int]: updated high score dictionary
    """

    today = datetime.datetime.now().isoformat()
    if len(high_score_dict) < 10:
        high_score_dict[today] = score
    else:
        min_date = min(high_score_dict, key=lambda k: high_score_dict[k])
        min_value = high_score_dict[min_date]
        if score > min_value:
            high_score_dict.pop(min_date)
            high_score_dict[today] = score
    return high_score_dict


@dataclass
class ItemsToRemove:
    bullets: set[int] = field(default_factory=set)
    invaders: set[tuple[int, int]] = field(default_factory=set)
    fortresses: set[int] = field(default_factory=set)


class App:
    def __init__(self):
        self.screen = t.Screen()
        self.screen.setup(width=Screen.WIDTH, height=Screen.HEIGHT)
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
        self.invaders: list[list[Invader]]
        self.invaders_movement_direction = InvadersMovementDirection.RIGHT
        self.initialize_invaders()
        self.bullets = []
        self.to_remove = ItemsToRemove()
        self.tasks = Queue()
        self.tasks_main = Queue()
        self.run = True
        self.fortresses: list[Fortress]
        self.cooldown_user_shoot = 0.5
        self.cooldown_user_last_shoot = perf_counter() - 30
        self.cooldown_invaders_shoot = 2
        self.cooldown_invaders_last_shoot = perf_counter()
        self.cooldown_invaders_movement = 2
        self.cooldown_invaders_last_move = perf_counter()
        self.cooldown_bullet_movement = 0.005
        self.cooldown_bullet_last_move = perf_counter()
        self.initialize_fortressesV2(-290)
        self.screen.onkey(
            lambda: (
                self.user.teleport(self.user.xcor() - 15)
                if self.user.xcor() - 15 > Screen.LEFT_LIMIT_FOR_OBJECTS
                else ...
            ),
            "Left",
        )
        self.screen.onkey(
            lambda: (
                self.user.teleport(self.user.xcor() + 15)
                if self.user.xcor() + 15 < Screen.RIGHT_LIMIT_FOR_OBJECTS
                else ...
            ),
            "Right",
        )
        self.screen.onkey(self.handle_user_shooting, "space")
        self.screen.onkey(self.stop, "q")

    # INITIALIZATION
    def initialize_invaders(self, top_row_y: numeric = 300, num_rows: int = 6) -> None:
        """Create instances of type Invaders. Fill screen with "enimies".
        <top_row_y> coresponds to the y coordinate of the top row. Number of rows is
        defined by parameter <num_rows>. <num_rows> must be a positiv integer.

        Keyword arguments:
        argument -- description
            top_row_y (numeric): Y coordinate for highes row is bots
            num_rows (int): number of rows
        Return: return_description
            None
        """

        if num_rows < 0:
            raise ValueError("Parameter num_rows must be a positive integer.")
        START_X = Screen.LEFT_LIMIT_FOR_OBJECTS
        END_X = int(Screen.WIDTH / 4)
        self.invaders_movement_direction = InvadersMovementDirection.RIGHT
        self.invaders = [
            [Invader(x, top_row_y - i * 40) for i in range(num_rows)]
            for x in range(START_X, END_X, 40)
        ]

    def initialize_fortresses(self, y: numeric, amount: int = 4) -> None:
        """Create instances of type Fortress building a secure shelter for user.
        Parameter <y> set a coordinate at which <amount> of instances will be
        positioned. <amount> must be positive integer.

        Keyword arguments:
        argument -- description
            y (numeric): coordinate to place fortresses
            amount (int): amount of fortresses.
        Return: return_description
            None
        """

        if amount < 0:
            raise ValueError(
                f"Parameter must be greater or equal null. Given: {amount}."
            )
        distance = int(Screen.WIDTH / (amount + 1))
        self.fortresses = [
            Fortress(x, y)
            for x in range(
                int(Screen.LEFT_LIMIT_FOR_OBJECTS) + distance,
                int(Screen.RIGHT_LIMIT_FOR_OBJECTS),
                distance,
            )
        ]

    def initialize_fortressesV2(self, y: numeric, amount: int = 4) -> None:
        """Create instances of type Fortress building a secure shelter for user.
        Parameter <y> set a coordinate at which <amount> of instances will be
        positioned. <amount> must be positive integer.

        Keyword arguments:
        argument -- description
            y (numeric): coordinate to place fortresses
            amount (int): amount of fortresses.
        Return: return_description
            None
        """

        if amount < 0:
            raise ValueError(
                f"Parameter must be greater or equal null. Given: {amount}."
            )
        distance = int(Screen.WIDTH / (amount + 1))
        self.fortresses = []
        for x in range(
            int(Screen.LEFT_LIMIT_FOR_OBJECTS) + distance,
            int(Screen.RIGHT_LIMIT_FOR_OBJECTS),
            distance,
        ):
            self.fortresses.append(Fortress(x - Fortress.radius, y))
            self.fortresses.append(Fortress(x + Fortress.radius, y))

    def remove_bullets(self) -> None:
        """Remove all bullets on the screen.
        Method is thread safe.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        if len(self.bullets) > 0:
            logger.debug("Reset list of bullets")
            [self.tasks_main.put(bullet.destroy) for bullet in self.bullets]
            rlock.acquire()
            self.to_remove.bullets.update([i for i in range(len(self.bullets))])
            rlock.release()

    # MOVEMENTS
    def move_invaders(self, sidestep: numeric = 15, forward_step: numeric = 30) -> None:
        """Handle movement of invaders on the screen.
        Paramers define length of each movement for all objects. Invaders move from
        left to right until the screen boarder. Then they step towards the user and
        change movement direction.

        Method has a colddown.

        Keyword arguments:
        argument -- description
            sidestep (numeric): length of the sidestep
            forward_step (numeric): length of the forward step
        Return: return_description
            None
        """

        if (
            perf_counter() - self.cooldown_invaders_last_move
            < self.cooldown_invaders_movement
        ):
            return
        self.cooldown_invaders_last_move = perf_counter()
        direction = self.invaders_movement_direction
        x_is_found = False
        x = None
        for row in self.invaders[:: direction * -1]:
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
        if (
            Screen.LEFT_LIMIT_FOR_OBJECTS
            < x + sidestep * direction
            < Screen.RIGHT_LIMIT_FOR_OBJECTS
        ):
            [
                [
                    item.teleport(item.xcor() + sidestep * direction, item.ycor())
                    for item in column
                    if item is not None
                ]
                for column in self.invaders
            ]
        else:
            self.invaders_movement_direction *= -1
            [
                [
                    item.teleport(item.xcor(), item.ycor() - forward_step)
                    for item in column
                    if item is not None
                ]
                for column in self.invaders
            ]

    def move_bullets(self) -> None:
        """Handle movements of the bullets on the screen.
        Step length for all bullets is set to 1.

        Method has a colddown.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        if (
            perf_counter() - self.cooldown_bullet_last_move
            < self.cooldown_bullet_movement
        ):
            return
        self.cooldown_bullet_last_move = perf_counter()
        [bullet.move(1) for bullet in self.bullets]

    # SHOOTING
    def handle_invaders_shooting(self) -> None:
        """Make invaders to shoot automaticaly.
        Find random invader in the top row and let it shoot. Shoots have a cooldown.
        Method is thread safe.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        if (
            perf_counter() - self.cooldown_invaders_last_shoot
            < self.cooldown_invaders_shoot
        ):
            return
        column = randint(0, len(self.invaders) - 1)
        for invader in self.invaders[column][::-1]:
            if invader is not None:
                rlock.acquire()
                self.bullets.append(invader.shoot())
                rlock.release()
                self.cooldown_invaders_last_shoot = perf_counter()
                return

    def handle_user_shooting(self, time_interval: numeric = 0.5) -> None:
        """Handle user's shooting process thread safe.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        if perf_counter() - self.cooldown_user_last_shoot > time_interval:
            rlock.acquire()
            self.bullets.append(self.user.shoot())
            rlock.release()
            self.cooldown_user_last_shoot = perf_counter()

    # CHECKS
    def handle_bullets_collisions(self, bullets_destroy_bullets: bool = False) -> None:
        """Handle bullet's collisions.
        If a distance between object and bullet is closer then radius of both objects,
        then application assumes a collision. Bullets and invaders disappear, user's and
        fortresses life points reduses. Parameter <bullets_destroy_bullets> configurates
        behaviour of the bullets when they are close to each other.

        Keyword arguments:
        argument -- description
            bullets_destroy_bullets (bool): flag
        Return: return_description
            None
        """

        for i, bullet in enumerate(self.bullets):
            if i in self.to_remove.bullets:
                continue
            if (self.user.xcor() - bullet.xcor()) ** 2 + (
                self.user.ycor() - bullet.ycor()
            ) ** 2 <= (
                self.user.radius + bullet.radius
            ) ** 2 and self.user.heading() != bullet.heading():
                logger.debug("Bullet hit user (%s, %s)", bullet.xcor(), bullet.ycor())
                self.to_remove.bullets.add(i)
                self.tasks_main.put(self.game_lifes.reduce_)
                self.tasks_main.put(self.game_lifes.update)
                self.tasks.put(self.remove_bullets)
            for fortress in self.fortresses:
                if (fortress.xcor() - bullet.xcor()) ** 2 + (
                    fortress.ycor() - bullet.ycor()
                ) ** 2 <= (fortress.radius + bullet.radius) ** 2:
                    logger.debug(
                        "Bullet hit fortress (%s, %s)", bullet.xcor(), bullet.ycor()
                    )
                    self.tasks.put(fortress.hit)
                    self.tasks_main.put(fortress.change_color)
                    self.tasks_main.put(bullet.destroy)
                    self.to_remove.bullets.add(i)
            for col, rows in enumerate(self.invaders):
                for row, invader in enumerate(rows):
                    if (
                        invader is not None
                        and (invader.xcor() - bullet.xcor()) ** 2
                        + (invader.ycor() - bullet.ycor()) ** 2
                        <= (invader.radius + bullet.radius) ** 2
                        and invader.heading() != bullet.heading()
                    ):
                        logger.debug(
                            "Bullet hit invader (%s, %s)", bullet.xcor(), bullet.ycor()
                        )
                        self.tasks_main.put(invader.destroy)
                        self.tasks_main.put(bullet.destroy)
                        self.to_remove.bullets.add(i)
                        self.tasks.put((lambda: self.game_score.increase(1)))
                        self.tasks_main.put(self.game_score.update)
                        self.to_remove.invaders.add((col, row))
            for n, other in enumerate(self.bullets):
                if (other.xcor() - bullet.xcor()) ** 2 + (
                    other.ycor() - bullet.ycor()
                ) ** 2 <= (
                    other.radius + bullet.radius
                ) ** 2 and other.heading() != bullet.heading():
                    logger.debug(
                        "Bullet hit bullet (%s, %s)", bullet.xcor(), bullet.ycor()
                    )
                    self.tasks_main.put(other.destroy)
                    self.tasks_main.put(bullet.destroy)
                    self.to_remove.bullets.add(i)
                    self.to_remove.bullets.add(n)
            if bullets_destroy_bullets:
                if (
                    bullet.ycor() < -Screen.HEIGHT / 2
                    or bullet.ycor() > Screen.HEIGHT / 2
                ):
                    self.to_remove.bullets.add(i)
                    self.tasks_main.put(bullet.destroy)

    def check_lifes_left(
        self,
    ) -> bool:
        """Method checks that user have enough life points to continue game.

        Keyword arguments:
        argument -- description
        Return: return_description
            Returns True when user have more then 0 life points otherwise False.
        """

        if self.game_lifes.value <= 0:
            logger.info("User lost all life points")
            return False
        return True

    def check_invaders_pass(self, y_cor: numeric = -280) -> bool:
        """Methode checks if invaders pass certain y coordinate and win. Coordinate is
        defined by parameter <y_cor>.

        Keyword arguments:
        argument -- description
            y_cor (numeric): cordinate that invaders must pass to win the game
        Return: return_description
            Returns True when first invader passed the <y_cor> otherwise False.
        """

        for column in self.invaders:
            for row in column:
                if row is not None:
                    if row.ycor() <= y_cor:
                        return True
        return False

    # UPDATE GAME STATE
    def reduce_cooldown(self) -> None:
        """Change cooldown values so the game seems to run faster.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        self.cooldown_bullet_movement -= 0.001
        self.cooldown_invaders_movement -= 0.03
        self.cooldown_user_shoot -= 0.009

    def handle_level_up(self) -> None:
        """Orcastrate tasks that are neccessary to start next game level.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        if self.game_level_up:
            self.game_level_up = False
            logger.debug("Updating level")
            self.tasks.put(self.remove_bullets)
            self.tasks.put((lambda: self.game_level.increase(1)))
            self.tasks_main.put(self.game_level.update)
            self.tasks_main.put(self.initialize_invaders)
            self.tasks.put(self.reduce_cooldown)
            logger.debug("Updated level")

    def show_game_over_label(self) -> None:
        """Show "GAME OVER" laber on the screen

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        GameOverLabel()

    def remove_destroyed_objects(self) -> None:
        """Remove marked objecsts from screen.

        Keyword arguments:
        argument -- description
        Return: return_description
            None
        """

        for item in ("fortresses", "bullets", "invaders"):
            if item in ("invaders",):
                lst = [
                    [
                        item
                        for row, item in enumerate(rows)
                        if (column, row) not in self.to_remove.invaders
                    ]
                    for column, rows in enumerate(self.invaders)
                ]
            else:
                lst = [
                    obj
                    for i, obj in enumerate(getattr(self, item))
                    if i not in getattr(self.to_remove, item)
                ]
            rlock.acquire()
            setattr(self, item, lst)
            rlock.release()
            rlock.acquire()
            getattr(self.to_remove, item).clear()
            rlock.release()

    def stop(self) -> None:
        logger.info("Stopping game...")
        self.run = False
