from typing import Protocol
import pytest
from turtle_invaders.app import (
    App,
)
from tests.test_spaceships import invader_fixture, Invader


class BulletProtocol(Protocol):
    def destroy(self) -> None: ...


@pytest.fixture
def app_fixture() -> App:
    return App()


def test_initialize_invaders(app_fixture: App) -> None:
    app_fixture.initialize_invaders()
    assert len(app_fixture.invaders) > 0


def test_initialize_fortresses(app_fixture: App) -> None:
    app_fixture.initialize_fortresses(300)
    assert len(app_fixture.fortresses) == 4


def test_initialize_fortressesV2(app_fixture: App) -> None:
    app_fixture.initialize_fortressesV2(300)
    assert len(app_fixture.fortresses) == 4 * 2


def test_remove_bullests(app_fixture: App) -> None:
    app_fixture.bullets.append(BulletProtocol)
    app_fixture.remove_bullets()
    assert app_fixture.tasks_main.qsize() == 1
    assert 0 in app_fixture.to_remove.bullets


@pytest.mark.parametrize("lifes, expected", ((4, True), (0, False)))
def test_check_lifes_left(app_fixture: App, lifes: int, expected: bool) -> None:
    app_fixture.game_lifes.value = lifes
    assert app_fixture.check_lifes_left() is expected


@pytest.mark.parametrize("y_cor, expected", ((-20, False), (20, True)))
def test_check_invaders_pass(
    app_fixture: App, invader_fixture: Invader, y_cor: int, expected: bool
) -> None:
    app_fixture.invaders = [[invader_fixture]]
    assert app_fixture.check_invaders_pass(y_cor) is expected
