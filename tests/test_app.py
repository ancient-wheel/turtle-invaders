import pytest
from tests.conftest import Bullet, Invader, App
from time import perf_counter


def test_initialize_invaders(app_fixture: App) -> None:
    app_fixture.initialize_invaders()
    assert len(app_fixture.invaders) > 0


def test_initialize_fortresses(app_fixture: App) -> None:
    app_fixture.initialize_fortresses(300, amount=4)
    assert len(app_fixture.fortresses) == 4


def test_initialize_fortressesV2(app_fixture: App) -> None:
    app_fixture.initialize_fortressesV2(300)
    assert len(app_fixture.fortresses) == 4 * 2


def test_mark_all_bullets_for_removal(app_fixture: App, bullet_fixture: Bullet) -> None:
    app_fixture.bullets.append(bullet_fixture)
    app_fixture.mark_all_bullets_for_removal()
    assert app_fixture.tasks_main.qsize() == 1
    assert bullet_fixture in app_fixture.garbage and len(app_fixture.garbage) == 1


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


def test_handle_level_up_permission_false(app_fixture: App) -> None:
    game_level = app_fixture.game_level.value
    app_fixture.handle_level_up()
    assert app_fixture.game_level.value == game_level


def test_handle_level_up_permission_true(app_fixture: App) -> None:
    app_fixture.game_level_up = True
    app_fixture.handle_level_up()
    assert not app_fixture.game_level_up


def test_collect_garbage(
    app_fixture: App, bullet_fixture: Bullet, invader_fixture: Invader, fortress_fixture
) -> None:
    app_fixture.bullets.append(bullet_fixture)
    app_fixture.invaders = [[invader_fixture]]
    app_fixture.fortresses = [fortress_fixture]
    app_fixture.garbage.update({bullet_fixture, invader_fixture, fortress_fixture})
    app_fixture.collect_garbage()
    assert bullet_fixture not in app_fixture.bullets
    assert invader_fixture not in app_fixture.invaders[0]
    assert fortress_fixture not in app_fixture.fortresses
    assert len(app_fixture.garbage) == 0


def test_handle_user_shooting(app_fixture: App) -> None:
    app_fixture.handle_user_shooting()
    assert len(app_fixture.bullets) == 1


def test_handle_user_shooting_on_cooldown(app_fixture: App) -> None:
    app_fixture.cooldown_user_last_shoot = perf_counter() + 10
    app_fixture.handle_user_shooting()
    assert len(app_fixture.bullets) == 0
