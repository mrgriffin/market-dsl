import __builtin__  # Unneeded once eval is separated.
from collections import namedtuple
from operator import attrgetter

from toolz.itertoolz import groupby
from singledispatch import singledispatch

from state import goal, state as football_state

partition = namedtuple('partition', ['coll', 'by'])
max = namedtuple('max', ['coll', 'key'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)

most_goals = max(partition(goals, 'team'), key=len)


@singledispatch
def eval(expr, env):
    raise NotImplementedError


@eval.register(max)
def eval_max(expr, env):
    # TODO: Support both teams having no goals.
    groups = groupby(expr.key, eval(expr.coll, env))
    return groups[__builtin__.max(groups)]


@eval.register(partition)
def eval_partition(expr, env):
    return groupby(attrgetter(expr.by), eval(expr.coll, env))


# TODO: Dispatch on collection type rather than "collection"?
@eval.register(collection)
def eval_collection(expr, env):
    # TODO: Avoid assuming env is a list of non-nested periods.
    incidents = (i for p in env for i in p.incidents)
    return (i for i in incidents if isinstance(i, expr.type))


print eval(most_goals, football_state)


@singledispatch
def typeof(expr):
    raise NotImplementedError


@typeof.register(max)
def typeof_max(expr):
    return [typeof(expr.coll).keys()[0]]


@typeof.register(partition)
def typeof_partition(expr):
    return {typeof(expr.by): typeof(expr.coll)}


@typeof.register(collection)
def typeof_collection(expr):
    return expr.type


# TODO: Have partition take an attr type as the "by".
@typeof.register(str)
def typeof_str(expr):
    return expr


print typeof(most_goals)
