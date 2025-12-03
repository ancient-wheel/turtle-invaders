import pytest
from turtle_invaders.fortresses import Fortress

VALID_PARAMETERS = (
    (0, 0),
    (0.0, 0.0),
    (0.0, 0),
    (0, 0.0),
)

INVALID_PARAMETERS = (
    (0, "0"),
    ("0", 0),
)

type numeric = int | float


@pytest.mark.parametrize("x, y", VALID_PARAMETERS)
def test_parametrized_valid_fortness(x: numeric, y: numeric) -> None:
    Fortress(x, y)


@pytest.mark.parametrize("x, y", INVALID_PARAMETERS)
def test_fortress_str_2(x: numeric, y: numeric) -> None:
    with pytest.raises(TypeError):
        dut = Fortress(x, y)


@pytest.fixture
def fortress_fixture() -> Fortress:
    return Fortress(0, 0)


def test_hit(fortress_fixture: Fortress) -> None:
    old_lifes = fortress_fixture.lifes
    fortress_fixture.hit()
    new_lifes = fortress_fixture.lifes
    assert old_lifes - new_lifes == 1


def test_change_color(fortress_fixture: Fortress) -> None:
    fortress_fixture.change_color()
    assert fortress_fixture.color()[0] == "blue"


def test_destroy(fortress_fixture: Fortress) -> None:
    fortress_fixture.destroy()
    assert fortress_fixture.isvisible() == False
