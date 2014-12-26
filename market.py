import __builtin__
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
    groups = groupby(expr.key, eval(expr.coll, env))
    return groups[__builtin__.max(groups)]


@eval.register(partition)
def eval_partition(expr, env):
    return groupby(attrgetter(expr.by), eval(expr.coll, env))


@eval.register(collection)
def eval_collection(expr, env):
    # TODO: Avoid assuming env is a list of non-nested periods.
    incidents = (i for p in env for i in p.incidents)
    return (i for i in incidents if isinstance(i, expr.type))


print eval(most_goals, football_state)
