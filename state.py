from collections import namedtuple

structure = namedtuple('structure', ['periods'])
period = namedtuple('period', ['exit', 'incidents'])

time = 'time'
goal = namedtuple('goal', ['team'])

football = structure((period(exit=time, incidents=(goal,)),) * 2)

print football
