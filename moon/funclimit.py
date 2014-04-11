# -*- coding: utf-8 -*-
from __future__ import absolute_import
import time
from functools import wraps


class LimitTimes(object):
    """ 限制函数在指定时间内执行次数
        times: 限制的次数
        spanseconds: 在多长的时间段内限制
        silence: 超出限制后是否静默返回None或者抛出异常
    """
    def __init__(self, times, spanseconds, silence=False):
        self.times = times
        self.spanseconds = spanseconds
        self.silence = silence
        self.history = []

    def require_call(self):
        curts = int(time.time())

        if self.spanseconds is not None:
            prets = curts - self.spanseconds
            fn = lambda h: h > prets
            self.history = filter(fn, self.history)

        if len(self.history) < self.times:
            self.history.append(curts)
            return True
        else:
            return False

    def __call__(self, func):
        @wraps(func)
        def decoed(*args, **kwargs):
            if self.require_call():
                return func(*args, **kwargs)
            else:
                if self.silence:
                    return None
                else:
                    raise RuntimeError("Out of call limits")
        return decoed


if __name__ == "__main__":

    @LimitTimes(3, 1, silence=True)
    def testfunc():
        return "OK"

    assert testfunc() == "OK"
    assert testfunc() == "OK"
    assert testfunc() == "OK"
    assert testfunc() is None

    time.sleep(2)
    
    assert testfunc() == "OK"

    print "passed"
