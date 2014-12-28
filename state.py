from collections import namedtuple


class Period(object):
    def __init__(self, incidents, open):
        self.incidents = incidents
        self.open = open

    def __repr__(self):
        return repr((self.incidents, self.open))


# TODO: Other attributes.  Rename team to participant.
State = namedtuple('State', ['teams', 'periods'])


def parse_state(structure, teams, incidents):
    # TODO: Verify that incidents matches the structure.
    periods = []
    for i in incidents:
        # TODO: Support nested periods.  Requires period-begin to carry
        #       a depth?
        if i is period.begin:
            periods.append(Period([], True))
        elif i is period.end:
            periods[-1].open = False
        else:
            periods[-1].incidents.append(i)
    return State(teams, periods)

structure = namedtuple('structure', ['periods'])
structure.__call__ = parse_state

period = namedtuple('period', ['exit', 'incidents'])
period.begin = 'PBEG'
period.end = 'PEND'

time = 'time'
goal = namedtuple('goal', ['team'])

football = structure((period(exit=time, incidents=(goal,)),) * 2)


incidents = [period.begin, goal('home'), period.end,
             period.begin, goal('away'), goal('home')]
state = football(['home', 'away'], incidents)
nil_state = football(['home', 'away'], [])
