import pytest
from turtle_invaders.scoreboard import (
    Score,
    LifeScore,
    Level,
)


@pytest.fixture
def score_fixture() -> Score:
    return Score()


def test_score_increase(score_fixture: Score) -> None:
    initial_value = score_fixture.value
    score_fixture.increase(10)
    assert score_fixture.value == initial_value + 10


@pytest.fixture
def life_score_fixture() -> LifeScore:
    return LifeScore()


def test_life_score_reduce(life_score_fixture: LifeScore) -> None:
    initial_value = life_score_fixture.value
    life_score_fixture.reduce_()
    assert life_score_fixture.value == initial_value - 1


@pytest.fixture
def level_fixture() -> Level:
    return Level()


def test_level_increase(level_fixture: Level) -> None:
    initial_value = level_fixture.value
    level_fixture.increase(1)
    assert level_fixture.value == initial_value + 1
