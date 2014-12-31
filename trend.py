from itertools import combinations
from operator import itemgetter

from singledispatch import singledispatch
from toolz.itertoolz import groupby

from market import walker
from result import eval, members
from selection import typeof


class rank(walker):
    def max(expr, env):
        coll = eval(expr.coll, env)

        groups = groupby(itemgetter(1), coll.iteritems())
        maxgroup = max(groups)
        unique_max = max(groups) + (len(groups[maxgroup]) != 1)

        keys = members(typeof(expr), env)

        def maxdiff(ks):
            if len(ks) > 1:
                return max(abs(coll[a] - coll[b])
                        for a, b in combinations(ks, 2))
            else:
                if coll[ks[0]] == unique_max:
                    return 0
                else:
                    # TODO: How does this math change for sports with non-1
                    #       scores (e.g. rugby)?
                    return 1 + maxgroup - coll[ks[0]]

        return {ks: maxdiff(ks) for ks in keys}

    # TODO: Avoid shadowing len and rank.
    def len(expr, env):
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
