# -*- coding: utf-8 -*-
class NameSpace(dict):
    """
    对dict的简单包装，可以使用`.`来访问数据
    """
    @classmethod
    def fromdict(cls, d):

        def wrapns(item):
            if isinstance(item, dict):
                item = cls(item)
                for k in item:
                    item[k] = wrapns(item[k])
            elif isinstance(item, (list, tuple)):
                item = map(wrapns, item)
            return item

        return wrapns(d)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value
