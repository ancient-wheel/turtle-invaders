import pytest
from typing import Protocol
from turtle_invaders.app import (
    App,
)
from turtle_invaders.spaceships import Invader


class BulletProtocol(Protocol):
    def destroy(self) -> None: ...


def test_initialize_invaders(app_fixture: App) -> None:
    app_fixture.initialize_invaders()
    assert len(app_fixture.invaders) > 0


def test_initialize_fortresses(app_fixture: App) -> None:
    app_fixture.initialize_fortresses(300, amount=4)
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


def test_reduce_cooldown(app_fixture: App) -> None:
    cooldown_bullet_movement_start = app_fixture.cooldown_bullet_movement
    cooldown_invaders_movement_start = app_fixture.cooldown_invaders_movement
    cooldown_user_shoot_start = app_fixture.cooldown_user_shoot
    app_fixture.reduce_cooldown(
        bullet_movement=0.001,
        inverders_movement=-0.03,
        user_shoot=0.009,
    )
    assert (
        cooldown_bullet_movement_start - app_fixture.cooldown_bullet_movement
        == pytest.approx(0.001)
    )
    assert (
        cooldown_invaders_movement_start - app_fixture.cooldown_invaders_movement
        == pytest.approx(0.03)
    )
    assert cooldown_user_shoot_start - app_fixture.cooldown_user_shoot == pytest.approx(
        0.009
    )


def test_stop(app_fixture: App) -> None:
    app_fixture.stop()
    assert app_fixture.run is False
