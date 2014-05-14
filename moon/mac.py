# -*- coding: utf-8 -*-
from os import system


def alert(msg, title=u'通知'):
    """
    osascript -e 'display notification "Lorem ipsum dolor sit amet"
    with title "Title"'
    """
    cmd = u"osascript -e 'display notification \"%s\" with title " \
          u"\"%s\"'" % (msg, title)
    print cmd
    system(cmd.encode("utf-8"))
