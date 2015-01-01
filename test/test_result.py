from random import randint, shuffle

from market import *
from state import football, period, goal
from result import eval as result

def gen_state(home, away):
    goals = [goal('home')] * home + [goal('away')] * away
    shuffle(goals)
    incidents = [period.begin] + goals
    return football(['home', 'away'], incidents)


def test_len():
    expr = len(goals)
    home = randint(0, 3)
    away = randint(0, 3)
    state = gen_state(home, away)
    assert result(expr, state) == home + away


def test_max():
    expr = max(map(partition(goals, 'team'), len))
    home = randint(0, 3)
    away = randint(0, 3)
    state = gen_state(home, away)
    expected = {-1: {'away'}, 0: {'home', 'away'}, 1: {'home'}}
    assert result(expr, state) == expected[cmp(home, away)]
