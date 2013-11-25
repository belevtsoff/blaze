# -*- coding: utf-8 -*-

"""
SciDB query generation and execution from Blaze AIR.
"""

from __future__ import print_function, division, absolute_import

from pykit.ir import interp

import blaze

from .error import SciDBError, InterfaceError
from .query import execute_query
from .datadesc import SciDBDataDesc

#------------------------------------------------------------------------
# Interpreter
#------------------------------------------------------------------------

def compile(func, env):
    # TODO: we can assemble a query at compile time, but we can't abstract
    # over scidb array names. Not sure this makes sense...
    return func, env

def interpret(func, env, args, persist=False, **kwds):
    # TODO: allow mixing scidb and non-scidb data...

    dshape = func.type.restype
    descs = [arg._data for arg in args]
    inputs = [desc.query for desc in descs]
    interfaces = [desc.interface for desc in descs]

    if len(set(interfaces)) > 1:
        raise InterfaceError(
            "Can only perform query over one scidb interface, got multiple")

    # Assemble query
    env = {'interp.handlers' : handlers}
    query = interp.run(func, env, None, args=inputs)

    # Execute query
    [interface] = set(interfaces)
    result = execute_query(interface, query, persist)
    return blaze.array(SciDBDataDesc(dshape, result))

#------------------------------------------------------------------------
# Handlers
#------------------------------------------------------------------------

def op_kernel(interp, funcname, *args):
    op = interp.op

    kernel   = op.metadata['kernel']
    overload = op.metadata['overload']

    func = overload.func
    return func(*args)

def op_convert(interp, arg):
    raise TypeError("scidb type conversion not supported yet")

def op_ret(interp, arg):
    interp.halt()
    return arg

handlers = {
    'kernel':   op_kernel,
    'convert':  op_convert,
    'ret':      op_ret,
}