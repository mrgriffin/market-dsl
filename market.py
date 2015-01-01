from collections import namedtuple
from itertools import chain, ifilter, imap

from singledispatch import singledispatch
from toolz.dicttoolz import valmap

from state import goal

operations = {op.__name__: op for op in (
    namedtuple('partition', ['coll', 'by']),
    namedtuple('len', ['coll']),
    namedtuple('max', ['coll']),
    namedtuple('map', ['coll', 'fn']),
    namedtuple('collection', ['type']),
    namedtuple('attr', ['elem', 'attr']),
    namedtuple('nth', ['coll', 'n']),
)}

collections = valmap(operations['collection'], {
    'goals': goal,
})

globals().update(operations)
globals().update(collections)
__all__ = operations.keys() + collections.keys()


# TODO: Should isinstance(..., walker) work?
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


def isoperation(expr):
    return expr in operations.viewvalues()


# TODO: Name this better.
def flatten(expr):
    subexprs = chain.from_iterable(ifilter(isoperation, expr))
    return {type(expr)} | set(imap(flatten, subexprs))


# TODO: Check for support for collection types, map functions etc.
def supports(walker, expr):
    ops = flatten(expr)
    return all(e in walker.registry for e in ops)
