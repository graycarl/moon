# -*- coding: utf-8 -*-
""" 这里是一些工具, 用来实现简单的项目配置系统 """
import logging

_confdata = {}


def setconf(prjname, confile, confdict={}):
    _confdata[prjname] = (confile, confdict)


def exportconf(prjname, globals):
    """ 从文件和字典中导出配置
    >>> open("/tmp/testmoonconf.py", "w").write("OSOS = 10")
    >>> setconf("hongbo", "/tmp/testmoonconf.py", {"OSOSOS": 321})
    >>> d = {}
    >>> exportconf("hongbo", d)
    >>> print d["OSOS"]
    10
    >>> print d["OSOSOS"]
    321
    """
    try:
        filename, confdict = _confdata[prjname]
    except KeyError as e:
        e.strerror = "Unable to find confdata for '%s', " \
                     "you must `setconf` first" % prjname
        raise
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, "exec"), globals)
            logging.info("Load config from %s", filename)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    if confdict:
        globals.update(confdict)


if __name__ == "__main__":
    import sys, os
    sys.path.remove(os.path.abspath(os.path.dirname(__file__)))
    import doctest
    doctest.testmod()
