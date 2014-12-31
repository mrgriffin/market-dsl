from itertools import chain, combinations
from operator import attrgetter, itemgetter

from singledispatch import singledispatch
from toolz.itertoolz import groupby

import market
from selection import typeof


# TODO: Swap parameter order for better partial application.
@singledispatch
def eval(expr, env):
    raise NotImplementedError


@eval.register(market.max)
def eval_max(expr, env):
    groups = groupby(itemgetter(1), eval(expr.coll, env).iteritems())
    return {k for k, v in groups[max(groups)]}


# TODO: Separate mapping and iterable len.
@eval.register(market.len)
def eval_len(expr, env):
    return sum(1 for _ in eval(expr.coll, env))


@eval.register(market.map)
def eval_map(expr, env):
    # TODO: Use eval_len.  Need to split AST eval from len calculation.
    fn = globals()['eval_map_' + expr.fn.__name__]
    return {k: fn(v) for k, v in eval(expr.coll, env).iteritems()}


def eval_map_len(coll):
    return sum(1 for _ in coll)


@eval.register(market.partition)
def eval_partition(expr, env):
    groups = groupby(attrgetter(expr.by), eval(expr.coll, env))
    return {k: groups.get(k, []) for k in members(typeof(expr.by), env)}


# TODO: Dispatch on collection type rather than "collection"?
@eval.register(market.collection)
def eval_collection(expr, env):
    # TODO: Avoid assuming env is a list of non-nested periods.
    incidents = (i for p in env.periods for i in p.incidents)
    return (i for i in incidents if isinstance(i, expr.type))


@singledispatch
def members(type, env):
    raise NotImplementedError


# TODO: This is the type of what max returns, which isn't quite a set.
@members.register(set)
def members_set(type, env):
    values = members(next(iter(type)), env)
    combs = (combinations(values, i)
             for i in xrange(1, len(values) + 1))
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
