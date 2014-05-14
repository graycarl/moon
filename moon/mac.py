# -*- coding: utf-8 -*-
# osascript -e 'tell app "System Events" to display dialog "Hello World"'
from os import system


def alert(msg):
    cmd = u"osascript -e 'tell app \"System Events\" to display " \
          "alert \"%s\"'" % msg
    system(cmd.encode("utf-8"))
