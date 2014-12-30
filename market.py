import __builtin__  # Unneeded once eval is separated.
from collections import namedtuple
from itertools import chain, combinations
from operator import attrgetter, itemgetter

import numpy as np
from toolz.itertoolz import groupby
from singledispatch import singledispatch

from state import goal, state as football_state, nil_state as football_nil

partition = namedtuple('partition', ['coll', 'by'])
len = namedtuple('len', ['coll'])
max = namedtuple('max', ['coll'])
map = namedtuple('map', ['coll', 'fn'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)

most_goals = max(map(partition(goals, 'team'), len))
total_goals = len(goals)


# TODO: Swap parameter order for better partial application.
@singledispatch
def eval(expr, env):
    raise NotImplementedError


@eval.register(max)
def eval_max(expr, env):
    groups = groupby(itemgetter(1), eval(expr.coll, env).iteritems())
    return {k for k, v in groups[__builtin__.max(groups)]}


# TODO: Separate mapping and iterable len.
@eval.register(len)
def eval_len(expr, env):
    return sum(1 for _ in eval(expr.coll, env))


@eval.register(map)
def eval_map(expr, env):
    # TODO: Use eval_len.  Need to split AST eval from len calculation.
    fn = globals()['eval_map_' + expr.fn.__name__]
    return {k: fn(v) for k, v in eval(expr.coll, env).iteritems()}


def eval_map_len(coll):
    return sum(1 for _ in coll)


@eval.register(partition)
def eval_partition(expr, env):
    groups = groupby(attrgetter(expr.by), eval(expr.coll, env))
    return {k: groups.get(k, []) for k in members(typeof(expr.by), env)}


# TODO: Dispatch on collection type rather than "collection"?
@eval.register(collection)
def eval_collection(expr, env):
    # TODO: Avoid assuming env is a list of non-nested periods.
    incidents = (i for p in env.periods for i in p.incidents)
    return (i for i in incidents if isinstance(i, expr.type))


@singledispatch
def typeof(expr):
    raise NotImplementedError


@typeof.register(max)
def typeof_max(expr):
    return {typeof(expr.coll).keys()[0]}


@typeof.register(len)
def typeof_len(expr):
    return int


@typeof.register(map)
def typeof_map(expr):
    # TODO: What should fn be instantiated with?
    coll = typeof(expr.coll)
    return {coll.keys()[0]: typeof(expr.fn(None))}


@typeof.register(partition)
def typeof_partition(expr):
    return {typeof(expr.by): typeof(expr.coll)}


@typeof.register(collection)
def typeof_collection(expr):
    return [expr.type]


# TODO: Have partition take an attr type as the "by".
@typeof.register(str)
def typeof_str(expr):
    return expr


@singledispatch
def members(type, env):
    raise NotImplementedError


# TODO: This is the type of what max returns, which isn't quite a set.
@members.register(set)
def members_set(type, env):
    values = members(next(iter(type)), env)
    combs = (combinations(values, i)
             for i in xrange(1, __builtin__.len(values) + 1))
    return list(chain.from_iterable(combs))


@members.register(str)
def members_str(type, env):
    return globals()['members_' + type](env)


# TODO: Return integral ranges as the type of expressions.  The range should
#       approximate sensible values for expressions of the preceeding type.
@members.register(type)
def members_int(type, env):
    return range(0, 10) + ['10+']


def members_team(env):
    return env.teams


@singledispatch
def rank(expr, env):
    raise NotImplementedError


@rank.register(max)
def rank_max(expr, env):
    coll = eval(expr.coll, env)

    groups = groupby(itemgetter(1), coll.iteritems())
    max = __builtin__.max(groups)
    unique_max = __builtin__.max(groups) + (__builtin__.len(groups[max]) != 1)

    keys = members(typeof(expr), env)

    def maxdiff(ks):
        if __builtin__.len(ks) > 1:
            return __builtin__.max(abs(coll[a] - coll[b])
                                   for a, b in combinations(ks, 2))
        else:
            if coll[ks[0]] == unique_max:
                return 0
            else:
                # TODO: How does this math change for sports with non-1
                #       scores (e.g. rugby)?
                return 1 + max - coll[ks[0]]

    return {ks: maxdiff(ks) for ks in keys}


@rank.register(len)
def rank_len(expr, env):
    len = eval(expr, env)

    def rank(l):
        if isinstance(l, str) and l.endswith('+'):
            return int(l[:-1]) - len
        elif l < len:
            # TODO: Is inf the right way to mark impossible outcomes?
            return float('inf')
        else:
            return l - len

    return {k: rank(k) for k in members(typeof(expr), env)}


def trend(expr, env0, env1):
    rank0 = rank(expr, env0)
    rank1 = rank(expr, env1)
    return {k: cmp(rank0[k], rank1[k]) for k in rank0}


def gfootball(env):
    goals_grid = np.array([
        [.2, .3, .1, .1],
        [.1, .1, .1, .0],
        [.0, .0, .0, .0],
        [.0, .0, .0, .0],
    ])

    @singledispatch
    def calculate(expr):
        raise NotImplementedError

    @calculate.register(len)
    def calculate_len(expr):
        grid = calculate(expr.coll)
        return {
            i: sum(grid[j, i - j] for j in xrange(0, i + 1))
            for i in xrange(0, grid.shape[0])
        }

    @calculate.register(map)
    def calculate_map(expr):
        assert expr.fn == len
        # TODO: Lift len into its own function.
        grid = calculate(expr.coll)
        return {
            k: {i: sum(grid[k][j, i - j] for j in xrange(0, i + 1))
                for i in xrange(0, grid[k].shape[0])}
            for k in grid
        }

    @calculate.register(partition)
    def calculate_partition(expr):
        # TODO: Support non-team partitioning.
        assert expr.by == 'team'
        grid = calculate(expr.coll)
        # TODO: Use masked arrays and share the data.
        home = np.zeros(grid.shape)
        draw = np.zeros(grid.shape)
        away = np.zeros(grid.shape)

        for i in xrange(0, grid.shape[0]):
            for j in xrange(0, grid.shape[1]):
                if i > j:
                    home[i, j] = grid[i, j]
                elif i == j:
                    draw[i, j] = grid[i, j]
                else:
                    away[i, j] = grid[i, j]

        return {('home',): home, ('home', 'away'): draw, ('away',): away}

    # TODO: Does this make sense?
    @calculate.register(max)
    def calculate_max(expr):
        grid = calculate(expr.coll)
        return {k: sum(v.itervalues()) for k, v in grid.iteritems()}

    @calculate.register(collection)
    def calculate_collection(expr):
        return goals_grid

    return calculate


print eval(most_goals, football_state)
print eval(most_goals, football_nil)
print typeof(most_goals)
print trend(most_goals, football_nil, football_state)
print trend(most_goals, football_nil, football_nil)

print eval(total_goals, football_state)
print eval(total_goals, football_nil)
print typeof(total_goals)
print trend(total_goals, football_nil, football_state)

calculate = gfootball(football_state)
print calculate(most_goals)
print calculate(total_goals)
