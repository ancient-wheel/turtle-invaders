import pytest
from collections.abc import Callable
from turtle_invaders.app import run_in_loop, App, perform_task_from
from queue import Queue
from time import perf_counter, sleep
import threading
from dataclasses import dataclass, field


class AppFixture:
    run: bool = True

def test_run_in_loop() -> None:
    counter = 0
    app = AppFixture()
    test_start = perf_counter()
    start_time = perf_counter()

    def increase_counter() -> None:
        nonlocal counter, start_time
        if perf_counter() - start_time > 1:
            counter += 1
            start_time = perf_counter()

    thread = threading.Thread(target=run_in_loop, args=(increase_counter, app))
    thread.start()
    while True:
        if perf_counter() - test_start >= 5:
            app.run = False
            break
        sleep(0.1)
    assert counter in (4, 5,6)


def test_perform_task_from() -> None:
    test_done = False
    test_queue = Queue()

    def test_task() -> None:
        nonlocal test_done
        test_done = True

    test_queue.put(test_task)
    perform_task_from(test_queue)
    assert test_done is True
    assert test_queue.qsize() == 0
