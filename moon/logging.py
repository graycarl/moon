#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging


def setlogging(logfile="debug.log"):
    fmt = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    if logfile:
        filename = os.path.abspath(os.path.join(os.getcwd(), "log", logfile))
        logging.basicConfig(filename=filename, format=fmt, level=logging.DEBUG)
    else:
        logging.basicConfig(format=fmt, level=logging.DEBUG)
