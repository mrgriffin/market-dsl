import numpy as np
from singledispatch import singledispatch

import market


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

    @calculate.register(market.len)
    def calculate_len(expr):
        grid = calculate(expr.coll)
        return {
            i: sum(grid[j, i - j] for j in xrange(0, i + 1))
            for i in xrange(0, grid.shape[0])
        }

    @calculate.register(market.map)
    def calculate_map(expr):
        assert expr.fn == market.len
        # TODO: Lift len into its own function.
        grid = calculate(expr.coll)
        return {
            k: {i: sum(grid[k][j, i - j] for j in xrange(0, i + 1))
                for i in xrange(0, grid[k].shape[0])}
            for k in grid
        }

    @calculate.register(market.partition)
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
    @calculate.register(market.max)
    def calculate_max(expr):
        grid = calculate(expr.coll)
        return {k: sum(v.itervalues()) for k, v in grid.iteritems()}

    @calculate.register(market.collection)
    def calculate_collection(expr):
        return goals_grid

    return calculate
