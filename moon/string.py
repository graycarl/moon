# -*- coding: utf-8 -*-
def truncate_unicode(s, length=50, ucas=2, end="..."):
    """ 把unicode字符串切断显示，非ascii字符算两个长度 """
    assert isinstance(s, unicode)
    if len(s) * 2 < length:
        return s
    curl = 0
    cs = []
    for c in s:
        if c > u'\u00ff':
            curl += ucas
        else:
            curl += 1
        if curl > length:
            break
        cs.append(c)
    return "".join(cs) + end
