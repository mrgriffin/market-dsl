import __builtin__  # Unneeded once eval is separated.
from collections import namedtuple
from itertools import chain, combinations
from operator import attrgetter

from toolz.dicttoolz import valmap
from toolz.itertoolz import groupby
from singledispatch import singledispatch

from state import goal, state as football_state, nil_state as football_nil

partition = namedtuple('partition', ['coll', 'by'])
max = namedtuple('max', ['coll', 'key'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)

most_goals = max(partition(goals, 'team'), key=len)


# TODO: Swap parameter order for better partial application.
@singledispatch
def eval(expr, env):
    raise NotImplementedError


# TODO: Remove key to avoid needing to pattern-match in max handlers.
@eval.register(max)
def eval_max(expr, env):
    def key((k, v)): return expr.key(v)
    groups = groupby(key, eval(expr.coll, env).iteritems())
    return {k for k, v in groups[__builtin__.max(groups)]}


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
    combs = (combinations(values, i) for i in xrange(1, len(values) + 1))
    return list(chain.from_iterable(combs))


@members.register(str)
def members_str(type, env):
    return globals()['members_' + type](env)


def members_team(env):
    return env.teams


@singledispatch
def rank(expr, env):
    raise NotImplementedError


@rank.register(max)
def rank_max(expr, env):
    coll = eval(expr.coll, env)

    def key((k, v)): return expr.key(v)
    groups = groupby(key, coll.iteritems())
    max = __builtin__.max(groups)
    unique_max = __builtin__.max(groups) + (len(groups[max]) != 1)

    keys = members(typeof(expr), env)
    values = valmap(expr.key, coll)

    def maxdiff(ks):
        try:
            return __builtin__.max(abs(values[a] - values[b])
                                   for a, b in combinations(ks, 2))
        except ValueError:
            if values[ks[0]] == unique_max:
                return 0
            else:
                # TODO: How does this math change for sports with non-1
                #       scores (e.g. rugby)?
                return 1 + max - values[ks[0]]

    return {ks: maxdiff(ks) for ks in keys}


def trend(expr, env0, env1):
    rank0 = rank(expr, env0)
    rank1 = rank(expr, env1)
    return {k: cmp(rank0[k], rank1[k]) for k in rank0}


print eval(most_goals, football_state)
print eval(most_goals, football_nil)
print typeof(most_goals)
print trend(most_goals, football_nil, football_state)
print trend(most_goals, football_nil, football_nil)
