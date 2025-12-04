import logging
from contextlib import suppress
import threading
from time import sleep
from pathlib import Path
from app import App, run_in_loop, perform_task_from
from scoreboard import CountDownLabel

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
high_score_path = (Path(__file__).parent / Path("..", "data", "highscore")).resolve()
with suppress(FileExistsError):
    high_score_path.mkdir(parents=True)


def main():
    logger.info("Starting game...")
    app = App()
    logger.info("Starting game... is done.")
    with suppress(FileNotFoundError):
        logger.debug("Searching for stored high score")
        with open(high_score_path) as f:
            logger.debug("Reading high score")
            app.game_high_score.value = int(f.read())
            app.game_high_score.update()
            logger.debug("Set high score")
        logger.debug("Searching for stored high score is done.")

    count_down = CountDownLabel()
    values = (3, 2, 1, "Go")
    values_iter = iter(values)
    for _ in range(len(values)):
        app.tasks_main.put((lambda: count_down.update(next(values_iter))))
        app.tasks_main.put(app.screen.update)
        app.tasks_main.put((lambda: sleep(1)))
    app.tasks_main.put(count_down.hide)
    while app.tasks_main.qsize() > 0:
        perform_task_from(app.tasks_main)
        sleep(0.001)
    logger.info("Starting thread with tasks...")
    th = threading.Thread(
        target=(lambda: run_in_loop(lambda: perform_task_from(app.tasks), app)),
        name="tasks",
    )
    th.start()
    logger.info("Start main thread...")
    while app.run:
        app.handle_invaders_shooting()
        app.move_invaders()
        app.move_bullets()
        app.handle_bullets_collisions()
        app.tasks.put(app.remove_destroy_objects)
        app.handle_level_up()
        perform_task_from(app.tasks_main)
        if app.check_invaders_pass() or not app.check_lifes_left():
            app.show_game_over_label()
            app.stop()
        app.screen.update()
        sleep(0.001)
    logger.info("Main thread is stopping...")
    logger.debug("Tasks thread is still alive? %s", th.is_alive())
    if app.check_invaders_pass() or not app.check_lifes_left():
        app.screen.exitonclick()
    logger.info("Saving high score...")
    if app.game_score.value > app.game_high_score.value:
        logger.debug("Score is higher then current high score.")
        with open(high_score_path, "w") as f:
            f.write(str(app.game_score.value))
            logger.debug("New high score is stored")
    logger.info("Saving high score... is done.")


if __name__ == "__main__":
    main()
