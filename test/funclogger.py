# -*- coding: utf-8 -*-
from moon.logging import FuncLogger, setlogging

setlogging(None)


from logging import getLogger
logger = getLogger("test.funclogger")

funclogger = FuncLogger(logger)


class ObjectA(object):
    @funclogger(printkey="b", withcaller=True)
    def funcinclass(self, a, b):
        pass


@funclogger(printkey=("a", "b"), withcaller=True)
def funcA(a=1, b=2):
    pass


@funclogger()
def funcB():
    funcA("haha")
    obja = ObjectA()
    obja.funcinclass("first", "second")


def main():
    funcB()
