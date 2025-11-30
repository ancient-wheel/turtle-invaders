import logging
from contextlib import suppress
import threading
from app import App, cyclic_execution, perform_tasks
from time import sleep
from scoreboard import CountDownText

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
        
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
    count_down = CountDownText()
    app.tasks_main.put((lambda: count_down.write_(3)))
    app.tasks_main.put((lambda: count_down.write_(2)))
    app.tasks_main.put((lambda: count_down.write_(1)))
    app.tasks_main.put((lambda: count_down.write_("Go")))
    app.tasks_main.put((lambda: count_down.write_("Go")))
    app.tasks_main.put(count_down.hide)
    while app.run:
        app.invaders_shoot()
        app.move_invaders()
        app.move_bullets()
        app.check_collisions()
        app.tasks.put(app.remove_items)
        app.increase_level()
        perform_tasks(app.tasks_main)
        if app.check_invaders_win() or not app.check_lifes_left():
            app.game_over()
            app.stop()
        app.screen.update()
        sleep(0.001)
    logger.info("Main thread is stopping...")
    logger.debug("Tasks thread is still alive? %s", th.is_alive())
    if app.check_invaders_win() or not app.check_lifes_left():
        app.screen.exitonclick()
    logger.info("Saving high score...")
    if app.game_score.value > app.game_high_score.value:
        logger.debug("Score is higher then current high score.")
        with open("highscore", "w") as f:
            f.write(str(app.game_score.value))
            logger.debug("New high score is stored")
    logger.info("Saving high score... is done.")
    
if __name__ == "__main__":
    main()
