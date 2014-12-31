from collections import namedtuple

from state import goal

partition = namedtuple('partition', ['coll', 'by'])
len = namedtuple('len', ['coll'])
max = namedtuple('max', ['coll'])
map = namedtuple('map', ['coll', 'fn'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)
