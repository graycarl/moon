# -*- coding: utf-8 -*-
import sqlalchemy
import sqlalchemy.orm
from math import ceil
from datetime import datetime
from time import mktime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.ext.declarative import declarative_base


__all__ = ["db", "BaseQuery"]


# 封装sqlalchemy的使用
# 大量参照了`Flask-SQLAlchemy`的实现
###############################################################################
def _include_sqlalchemy(obj):
    for module in (sqlalchemy, sqlalchemy.orm):
        for key in module.__all__:
            if key is ["Session"]:
                continue
            setattr(obj, key, getattr(module, key))


class Pagination(object):
    """ 分页组件 """
    def __init__(self, query, page_num, per_page, total, items):
        self.query = query
        self.page_num = page_num
        self.per_page = per_page
        self.items = items
        self.total = total

    @property
    def pages(self):
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        assert self.query is not None, "a query object is required " \
                                       "for this method work."
        return self.query.paginate(self.page_num-1, self.per_page, error_out)

    @property
    def prev_num(self):
        return self.page_num - 1

    @property
    def has_prev(self):
        return self.page_num > 1

    def next(self, error_out=False):
        assert self.query is not None, "a query object is required " \
                                       "for this method work."
        return self.query.paginate(self.page_num+1, self.per_page, error_out)

    @property
    def next_num(self):
        return self.page_num + 1

    @property
    def has_next(self):
        return self.page_num < self.pages


class BaseQuery(sqlalchemy.orm.Query):
    """ 扩展默认:class:`query`，添加:method:`paginate`方法 """
    def paginate(self, page_num, per_page, error_out=False):
        """
        @error_out: 当没有元素的时候，是否raise
        返回一个:class:`Pagination`对象
        """
        if page_num < 1 and error_out:
            raise error_out
        items = self.limit(per_page) \
            .offset((page_num - 1) * per_page).all()

        if not items and page_num != 1 and error_out:
            raise error_out

        if page_num == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page_num, per_page, total, items)


class _QueryProperty(object):
    """ descriptor for model.query """
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = sqlalchemy.orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


class Model(object):
    query_class = BaseQuery
    query = None

    def to_dict(self, *columns):
        dct = {}
        for c in columns:
            d = getattr(self, c)
            if isinstance(d, datetime):
                dct[c] = d
                dct[c + "_str"] = d.strftime("%Y-%m-%d %H:%M:%S")
                dct[c + "_ts"] = int(mktime(d.timetuple()))
            else:
                dct[c] = d
        return dct

    def cs_update(self, **kwargs):
        """ 批量修改属性值
        :**kwargs: 属性值的dict
        """
        for k in self._csupdate_keys:
            if k in kwargs:
                setattr(self, k, kwargs[k])
        if hasattr(self, "update_time"):
            self.update_time = datetime.utcnow()


class SQLAlchemy(object):
    """ 对sqlalchemy使用的封装 """
    _Session = None

    def __init__(self):
        _include_sqlalchemy(self)
        self.Model = self.make_declarative_base()

    def make_declarative_base(self):
        base = declarative_base(cls=Model, name="Model")
        base.query = _QueryProperty(self)
        return base

    @property
    def session(self):
        return self._Session

    @session.setter
    def set_Session(self, S):
        assert self._Session is None, "Session already setted"
        self._Session = S

    def use_scoped_session(self, engine=None):
        if not engine:
            from ..config import get_config
            config = get_config()
            dburl = config.SQLALCHEMY_DATABASE_URI
            dbecho = config.SQLALCHEMY_ECHO
            engine = create_engine(dburl, echo=dbecho)

        session_factory = sessionmaker(bind=engine)
        self._Session = scoped_session(session_factory)
        self._engine = engine

    def create_all(self):
        self.Model.metadata.create_all(bind=self._engine)

    def drop_all(self):
        self.Model.metadata.drop_all(bind=self._engine)


db = SQLAlchemy()
