import pytest
from turtle_invaders.bullet import Bullet


def test_move(bullet_fixture: Bullet) -> None:
    bullet_fixture.move(10)
    assert bullet_fixture.xcor() == pytest.approx(0.0)
    assert bullet_fixture.ycor() == pytest.approx(10.0)


def test_destroy(bullet_fixture: Bullet) -> None:
    bullet_fixture.destroy()
    assert bullet_fixture.isvisible() is False
