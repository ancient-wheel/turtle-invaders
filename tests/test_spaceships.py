import pytest
from turtle_invaders.spaceships import SpaceShip, Invader
from turtle_invaders.constants import ObjectDirection

type numeric = int | float


@pytest.fixture
def spaceship_fixture() -> SpaceShip:
    return SpaceShip()


def test_spaceship_shoot(spaceship_fixture: SpaceShip) -> None:
    bullet = spaceship_fixture.shoot()
    assert bullet.xcor() == spaceship_fixture.xcor()
    assert bullet.ycor() == spaceship_fixture.ycor()
    assert bullet.color()[0] == "green"
    assert bullet.heading() == ObjectDirection.NORTH


@pytest.fixture
def invader_fixture() -> Invader:
    return Invader(0, 0)


def test_invader_shoot(invader_fixture: Invader) -> None:
    bullet = invader_fixture.shoot()
    assert bullet.xcor() == invader_fixture.xcor()
    assert bullet.ycor() == invader_fixture.ycor()
    assert bullet.color()[0] == invader_fixture.color()[0]
    assert bullet.heading() == ObjectDirection.SOUTH


def test_destroy(invader_fixture: Invader) -> None:
    invader_fixture.destroy()
    assert invader_fixture.isvisible() == False
