from singledispatch import singledispatch

import market


@singledispatch
def typeof(expr):
    raise NotImplementedError


@typeof.register(market.max)
def typeof_max(expr):
    return {typeof(expr.coll).keys()[0]}


@typeof.register(market.len)
def typeof_len(expr):
    return int


@typeof.register(market.map)
def typeof_map(expr):
    # TODO: What should fn be instantiated with?
    coll = typeof(expr.coll)
    return {coll.keys()[0]: typeof(expr.fn(None))}


@typeof.register(market.partition)
def typeof_partition(expr):
    return {typeof(expr.by): typeof(expr.coll)}


@typeof.register(market.collection)
def typeof_collection(expr):
    return [expr.type]


# TODO: Have partition take an attr type as the "by".
@typeof.register(str)
def typeof_str(expr):
    return expr
