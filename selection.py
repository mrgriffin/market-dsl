from singledispatch import singledispatch

from market import walker


class typeof(walker):
    def max(expr):
        return {typeof(expr.coll).keys()[0]}

    def len(expr):
        return int

    def map(expr):
        # TODO: What should fn be instantiated with?
        coll = typeof(expr.coll)
        return {coll.keys()[0]: typeof(expr.fn(None))}

    def partition(expr):
        return {typeof(expr.by): typeof(expr.coll)}

    def collection(expr):
        return [expr.type]


# TODO: Have partition take an attr type as the "by".
# TODO: Avoid requiring that walkers are implemented with singledispatch.
@typeof.register(str)
def typeof_str(expr):
    return expr
