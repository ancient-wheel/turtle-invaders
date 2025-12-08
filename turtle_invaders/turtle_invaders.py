import logging
from contextlib import suppress
import threading
from time import sleep
from pathlib import Path
from app import App, run_in_loop, perform_task_from, read_json, write_json, add_score
from scoreboard import CountDownLabel

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
high_score_path = (
    Path(__file__).parent / Path("..", "data", "highscore.json")
).resolve()
high_score_path.parent.mkdir(parents=True, exist_ok=True)


def main():
    logger.info("Starting game...")
    app = App()
    logger.info("Starting game... is done.")
    results = read_json(high_score_path)
    max_score = None
    with suppress(ValueError):
        max_score = max(results.values())
    app.game_high_score.value = max_score if max_score is not None else 0
    app.tasks_main.put(app.game_high_score.update)

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
        app.tasks.put(app.remove_destroyed_objects)
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
    results = read_json(high_score_path)
    new_results = add_score(results, app.game_score.value)
    write_json(new_results, high_score_path)
    logger.info("Saving high score... is done.")


if __name__ == "__main__":
    main()
