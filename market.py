import __builtin__  # Unneeded once eval is separated.
from collections import namedtuple
from operator import attrgetter

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


def members(type, env):
    """Returns the members of a type."""
    return globals()['members_' + type](env)


def members_team(env):
    return env.teams


print eval(most_goals, football_state)
print eval(most_goals, football_nil)
print typeof(most_goals)
