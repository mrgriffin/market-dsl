from collections import namedtuple

from singledispatch import singledispatch
from toolz.dicttoolz import valmap

from state import goal

operations = {op.__name__: op for op in (
    namedtuple('partition', ['coll', 'by']),
    namedtuple('len', ['coll']),
    namedtuple('max', ['coll']),
    namedtuple('map', ['coll', 'fn']),
    namedtuple('collection', ['type']),
)}

collections = valmap(operations['collection'], {
    'goals': goal,
})

globals().update(operations)
globals().update(collections)
__all__ = operations.keys() + collections.keys()

class walker(object):
    class __metaclass__(type):
        def __new__(cls, name, bases, attrs):
            # Make walker a regular class so it can be subclassed.
            if bases == (object,):
                return type.__new__(cls, name, bases, attrs)

            @singledispatch
            def dispatch(*args):
                raise NotImplementedError

            dispatch.__name__ = name
            dispatch.__doc__ = attrs.get('__doc__')

            for name, attr in attrs.iteritems():
                if not name.startswith('__'):
                    dispatch.register(operations[name])(attr)

            return dispatch
