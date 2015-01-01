import numpy as np

import market
from market import walker


def gfootball(env):
    goals_grid = np.array([
        [.2, .3, .1, .1],
        [.1, .1, .1, .0],
        [.0, .0, .0, .0],
        [.0, .0, .0, .0],
    ])

    class calculate(walker):
        def len(expr):
            grid = calculate(expr.coll)
            return {
                i: sum(grid[j, i - j] for j in xrange(0, i + 1))
                for i in xrange(0, grid.shape[0])
            }

        def map(expr):
            assert expr.fn == market.len
            # TODO: Lift len into its own function.
            grid = calculate(expr.coll)
            return {
                k: {i: sum(grid[k][j, i - j] for j in xrange(0, i + 1))
                    for i in xrange(0, grid[k].shape[0])}
                for k in grid
            }

        def partition(expr):
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
        def max(expr):
            grid = calculate(expr.coll)
            return {k: sum(v.itervalues()) for k, v in grid.iteritems()}

        def collection(expr):
            return goals_grid

        def nth(expr):
            grid = calculate(expr.coll)
            nth = np.zeros(grid.shape)
            n = expr.n + 1
            for i in xrange(0, n + 1):
                nth[i, n - i] = grid[i, n - i]
            nth *= 1 / np.sum(nth)
            return nth

        # HINT: This would explode for all goals after the first because
        #       the diagonal will have a value.  The diagonals need to be
        #       converted into a home and an away value.
        def attr(expr):
            assert expr.attr == 'team'
            grid = calculate(expr.elem)
            # TODO: Use partition to do the heavy lifting.
            home = 0
            away = 0
            for i in xrange(0, grid.shape[0]):
                for j in xrange(0, grid.shape[1]):
                    if i > j:
                        home += grid[i, j]
                    elif j > i:
                        away += grid[i, j]
                    else:
                        assert grid[i, j] == 0

            return {'home': home, 'away': away}

    return calculate
