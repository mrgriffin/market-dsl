from random import randint, shuffle

from market import *
from state import football, period, goal
from result import eval as result

def gen_state(home, away):
    goals = [goal('home')] * home + [goal('away')] * away
    shuffle(goals)
    incidents = [period.begin] + goals
    return football(['home', 'away'], incidents)


def test():
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


    def test_attr():
        expr = attr(nth(goals, 0), 'team')
        home = randint(0, 1)
        away = randint(0, 1 - home)
        state = gen_state(home, away)
        expected = {(0, 0): None, (1, 0): 'home', (0, 1): 'away'}
        assert result(expr, state) == expected[(home, away)]

    for _ in xrange(100):
        yield test_len
        yield test_max
        yield test_attr
