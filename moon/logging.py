#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging
import inspect
from pprint import pformat
from functools import wraps

__all__ = ["setlogging", "FuncLogger"]


def setlogging(logfile="debug.log"):
    fmt = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    if logfile:
        filename = os.path.abspath(os.path.join(os.getcwd(), "log", logfile))
        logging.basicConfig(filename=filename, format=fmt, level=logging.DEBUG)
    else:
        logging.basicConfig(format=fmt, level=logging.DEBUG)


class FuncLogger(object):
    """ 将函数的被调用记录写入日志 """
    def __init__(self, logger, level=logging.DEBUG):
        self._logger = logger
        self._level = level

    def log(self, msg, *args, **kwargs):
        self._logger.log(self._level, msg, *args, **kwargs)

    def __call__(self, printkey=None, repr=pformat, withcaller=False):
        def deco_func(func):
            @wraps(func)
            def decoed(*args, **kwargs):
                try:
                    callargs = inspect.getcallargs(func, *args, **kwargs)
                    names = []
                    if "self" in callargs:
                        _class = callargs["self"].__class__
                        names.append(_class.__module__)
                        names.append(_class.__name__)
                    else:
                        names.append(func.__module__)
                    names.append(func.__name__)
                    funcname = ".".join(names)
                    self.log("FuncLogger: [%s] was called", funcname)

                    if printkey:
                        keys = printkey
                        if not isinstance(printkey, (list, tuple)):
                            keys = [printkey]
                        for key in keys:
                            value = callargs[key]
                            self.log("   |______: with argument %s => %s",
                                     key, repr(value))
                    
                    if withcaller:
                        funcname = caller_name(2)
                        self.log("   |______: caller is [%s]", funcname)

                except Exception as e:
                    self.log("FuncLogger Error: %s", e)
                finally:
                    return func(*args, **kwargs)
            return decoed
        return deco_func


def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height

       from https://gist.github.com/2151727
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]    

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return ".".join(name)
