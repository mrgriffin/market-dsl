from collections import namedtuple

from singledispatch import singledispatch

from state import goal

partition = namedtuple('partition', ['coll', 'by'])
len = namedtuple('len', ['coll'])
max = namedtuple('max', ['coll'])
map = namedtuple('map', ['coll', 'fn'])

# TODO: Add missing attributes.
collection = namedtuple('collection', ['type'])
goals = collection(goal)

class walker(object):
    class __metaclass__(type):
        def __new__(cls, name, bases, methods):
            # Make walker a regular class so it can be subclassed.
            if bases == (object,):
                return type.__new__(cls, name, bases, methods)

            @singledispatch
            def dispatch(*args):
                raise NotImplementedError

            for name, method in methods.iteritems():
                if not name.startswith('__'):
                    dispatch.register(globals()[name])(method)

            return dispatch
