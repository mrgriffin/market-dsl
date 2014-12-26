from collections import namedtuple

from state import goal

partition = namedtuple('partition', ['coll', 'by'])
max = namedtuple('max', ['coll', 'key'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)

most_goals = max(partition(goals, 'team'), key=len)

print most_goals
