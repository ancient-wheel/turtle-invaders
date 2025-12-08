import json
from pathlib import Path
from queue import Queue
from time import perf_counter, sleep
import threading
from typing import Protocol
import pytest
import tempfile
import datetime as dt
from turtle_invaders.app import (
    run_in_loop,
    perform_task_from,
    write_json,
    read_json,
    add_score,
)


class AppProtocol(Protocol):
    run: bool = True


class FileProcotol(Protocol):
    name: str


@pytest.fixture
def app_fixture() -> AppProtocol:
    return AppProtocol()


def test_run_in_loop(app_fixture: AppProtocol) -> None:
    counter = 0
    app = app_fixture
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
def json_file_fixture() -> FileProcotol:
    with tempfile.NamedTemporaryFile(suffix=".json", delete_on_close=False) as file:
        return file


@pytest.fixture
def txt_file_fixture() -> FileProcotol:
    with tempfile.NamedTemporaryFile(suffix=".txt") as file:
        return file


@pytest.fixture
def dictionary_fixture() -> dict[str, int]:
    return {
        dt.date(2024, 10, 3).isoformat(): 105,
        dt.date(2023, 4, 6).isoformat(): 20,
    }


def test_write_json_json_file(
    dictionary_fixture: dict[str, int],
    json_file_fixture: FileProcotol,
) -> None:
    write_json(dictionary_fixture, json_file_fixture.name)
    with open(json_file_fixture.name, "r") as f:
        result = json.load(f)
        assert dictionary_fixture == result


def test_write_json_txt_file(
    dictionary_fixture: dict[str, int],
    txt_file_fixture: FileProcotol,
) -> None:
    write_json(dictionary_fixture, txt_file_fixture.name)
    json_path = Path(txt_file_fixture.name).with_suffix(".json")
    with open(json_path, "r") as f:
        result = json.load(f)
        assert dictionary_fixture == result


def test_read_json_missing_file() -> None:
    result = read_json("test.json")
    assert result == {}


def test_read_json(
    dictionary_fixture: dict[str, int],
    json_file_fixture: fileProcotol,
) -> None:
    with open(json_file_fixture.name, "w") as f:
        json.dump(dictionary_fixture, f)
    json_path = Path(json_file_fixture.name)
    result = read_json(json_path)
    assert result == dictionary_fixture


@pytest.fixture
def high_score_fixture() -> dict[str, int]:
    return {
        "2024-10-01T12:00:00.000000": 150,
        "2024-09-30T13:59:00.000000": 120,
        "2024-09-29T14:01:00.000000": 110,
        "2024-09-28T23:00:00.000000": 100,
        "2024-09-27T08:01:00.000000": 90,
        "2024-09-26T10:04:00.000000": 80,
        "2024-09-25T11:33:00.000000": 70,
        "2024-09-24T11:35:00.000000": 60,
        "2024-09-23T20:00:00.000000": 50,
    }


def test_add_score(high_score_fixture: dict[str, int]) -> None:
    # Test adding a score when there are less than 10 scores
    updated_scores = add_score(high_score_fixture, 85)
    assert len(updated_scores) == 10
    assert any(score == 85 for score in updated_scores.values())
    assert any(score == 50 for score in updated_scores.values())

    # Test adding a score when there are already 10 scores
    # Adding a higher score
    updated_scores_10 = add_score(updated_scores.copy(), 95)
    assert all(score != 50 for score in updated_scores_10.values())
    # Adding a lower score
    updated_scores_11 = add_score(updated_scores.copy(), 45)
    assert updated_scores == updated_scores_11
