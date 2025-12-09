import json
import logging
import threading
import datetime
from contextlib import suppress
from time import sleep
from pathlib import Path
from collections.abc import Callable
from queue import Queue
from .app import App

logger = logging.getLogger(__name__)


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
