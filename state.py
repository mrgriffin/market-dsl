from collections import namedtuple


class Period(object):
    def __init__(self, incidents, open):
        self.incidents = incidents
        self.open = open

    def __repr__(self):
        return repr((self.incidents, self.open))


def parse_state(structure, incidents):
    # TODO: Verify that incidents matches the structure.
    state = []
    for i in incidents:
        # TODO: Support nested periods.  Requires period-begin to carry
        #       a depth?
        if i is period.begin:
            state.append(Period([], True))
        elif i is period.end:
            state[-1].open = False
        else:
            state[-1].incidents.append(i)
    return state

structure = namedtuple('structure', ['periods'])
structure.__call__ = parse_state

period = namedtuple('period', ['exit', 'incidents'])
period.begin = 'PBEG'
period.end = 'PEND'

time = 'time'
goal = namedtuple('goal', ['team'])

football = structure((period(exit=time, incidents=(goal,)),) * 2)


incidents = [period.begin, goal('home'), period.end,
             period.begin, goal('away')]
state = football(incidents)
