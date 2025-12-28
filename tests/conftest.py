import pytest
from turtle_invaders.app import App
from turtle_invaders.spaceships import SpaceShip, Invader
from turtle_invaders.bullet import Bullet
from turtle_invaders.fortresses import Fortress
from turtle_invaders.constants import ObjectDirection


@pytest.fixture
def spaceship_fixture() -> SpaceShip:
    return SpaceShip()


@pytest.fixture
def invader_fixture() -> Invader:
    return Invader(0, 0)


@pytest.fixture
def app_fixture() -> App:
    return App()


@pytest.fixture
def bullet_fixture() -> Bullet:
    return Bullet(0, 0, ObjectDirection.NORTH, "white")


@pytest.fixture
def fortress_fixture() -> Fortress:
    return Fortress(0, 0)
