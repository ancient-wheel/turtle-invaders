import json
from pathlib import Path
from queue import Queue
from time import perf_counter, sleep
import threading
import pytest
import tempfile
from turtle_invaders.app import (
    run_in_loop,
    perform_task_from,
    write_json,
    read_json,
)


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
    assert counter in (4, 5, 6)


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


@pytest.fixture
def json_file_fixture():
    with tempfile.NamedTemporaryFile(suffix=".json", delete_on_close=False) as file:
        return file


@pytest.fixture
def txt_file_fixture():
    with tempfile.NamedTemporaryFile(suffix=".txt") as file:
        return file


@pytest.fixture
def dictionary_fixture() -> dict[str, int]:
    return {
        "1": 933,
        "2": 20,
    }


def test_write_json_json_file(dictionary_fixture, json_file_fixture):
    write_json(dictionary_fixture, json_file_fixture.name)
    with open(json_file_fixture.name, "r") as f:
        result = json.load(f)
        assert dictionary_fixture == result


def test_write_json_txt_file(dictionary_fixture, txt_file_fixture):
    write_json(dictionary_fixture, txt_file_fixture.name)
    json_path = Path(txt_file_fixture.name).with_suffix(".json")
    with open(json_path, "r") as f:
        result = json.load(f)
        assert dictionary_fixture == result


def test_read_json_missing_file():
    result = read_json("test.json")
    assert result == {}


def test_read_json(dictionary_fixture, json_file_fixture):
    with open(json_file_fixture.name, "w") as f:
        json.dump(dictionary_fixture, f)
    json_path = Path(json_file_fixture.name)
    result = read_json(json_path)
    assert result == dictionary_fixture
