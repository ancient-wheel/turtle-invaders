from turtle_invaders.fortresses import Fortress
from pytest import fixture
from pytest import raises

def test_fortress_float():
    dut = Fortress(0.0, 0.0)
    assert isinstance(dut, Fortress)

def test_fortress_int():
    dut = Fortress(0, 0)
    assert isinstance(dut, Fortress)
    
def test_fortress_str_1():
    with raises(TypeError):
        dut = Fortress("0", 0)

def test_fortress_str_2():
    with raises(TypeError):
        dut = Fortress(0, "0")

@fixture
def test_fortress_fixture():
    return Fortress(0, 0)
    
def test_hit(test_fortress_fixture):
    old_lifes = test_fortress_fixture.lifes
    test_fortress_fixture.hit()
    new_lifes = test_fortress_fixture.lifes
    assert old_lifes - new_lifes == 1
    
def test_change_color(test_fortress_fixture):
    test_fortress_fixture.change_color()
    assert test_fortress_fixture.color()[0] == "blue"

def test_destroy(test_fortress_fixture):
    test_fortress_fixture.destroy()
    assert test_fortress_fixture.isvisible() == False