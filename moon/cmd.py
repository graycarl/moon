# -*- coding: utf-8 -*-
import sys


class ProgressBar(object):
    def __init__(self, prefix=u'Progress', max=100, percent=False, clen=30):
        self.prefix = prefix
        self.max = max
        self.percent = percent
        self.clen = clen

    def build_bar(self, current):
        ccur = int(self.clen * current / self.max)
        out = "#"*ccur + " "*(self.clen-ccur)
        return out

    def build_suffix(self, current):
        if self.percent:
            p = int(100 * current / self.max)
            return "%d%%" % p
        else:
            return "%d/%d" % (current, self.max)

    def __call__(self, current, exinfo=""):
        fmt = "\r%s [%s] %s %s"
        bar = self.build_bar(current)
        suffix = self.build_suffix(current)
        line = fmt % (self.prefix.encode("utf-8"), bar, suffix, exinfo)
        sys.stdout.write(line)
        sys.stdout.flush()


if __name__ == "__main__":
    import time

    print "Progress bar not percent, max=234"
    bar = ProgressBar(prefix=u'进度', max=234)
    for cur in range(0, 234, 3):
        bar(cur)
        time.sleep(0.1)
    print "END"
    print
    print "Progress bar percent, max=432"
    bar = ProgressBar(max=432, percent=True, clen=40)
    for cur in range(0, 432, 5):
        bar(cur, u"哈哈")
        time.sleep(0.1)
