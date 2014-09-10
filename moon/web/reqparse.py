# -*- coding: utf-8 -*-
import re
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest
import six
from datetime import datetime


class NameSpace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class ArgumentError(ValueError):
    def __init__(self, arg, msg):
        super(ArgumentError, self).__init__(msg)
        self.source = arg


class Argument(object):
    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=six.text_type, location=("values",),
                 choices=(), action="store", help=None, operators=("=",),
                 case_sensitive=True, max_len=800, min_len=0, max_count=None,
                 min_count=None):
        self.name = name
        self.default = default
        self.dest = dest
        self.required = required
        self.ignore = ignore
        self.type = type
        self.location = location
        self.choices = choices
        self.action = action
        self.help = help
        self.operators = operators
        self.case_sensitive = case_sensitive
        self.max_len = max_len
        self.min_len = min_len
        self.max_count = max_count
        self.min_count = min_count

    def source(self, request):
        if isinstance(self.location, six.string_types):
            value = getattr(request, self.location, MultiDict())
            if value is not None:
                return value
        else:
            for l in self.location:
                value = getattr(request, l, None)
                if value is not None:
                    return value
        return MultiDict()

    def convert(self, value, op):
        if len(value) > self.max_len or len(value) < self.min_len:
            raise ValueError(
                "value length {0} out of limit -- max:{1} min:{2}"
                .format(len(value), self.max_len, self.min_len)
            )
        try:
            return self.type(value, self.name, op)
        except TypeError:
            try:
                return self.type(value, self.name)
            except TypeError:
                return self.type(value)

    def handle_validation_error(self, error):
        msg = self.help if self.help is not None else unicode(error)
        raise ArgumentError(self, msg)

    def parse(self, request):
        source = self.source(request)

        results = []

        for operator in self.operators:
            name = self.name + operator.replace("=", "", 1)
            if name in source:
                if hasattr(source, "getlist"):
                    values = source.getlist(name)
                else:
                    values = [source.get(name)]

                for value in values:
                    if not self.case_sensitive:
                        value = value.lower()
                    if self.choices and value not in self.choices:
                        self.handle_validation_error(
                            ValueError(
                                u'{0} is not valid choice'.format(value))
                        )
                    try:
                        value = self.convert(value, operator)
                    except Exception as error:
                        if self.ignore:
                            continue

                        self.handle_validation_error(error)
                    results.append(value)

        if not results and self.required:
            if isinstance(self.location, six.string_types):
                error_msg = u"{0} is required in {1}".format(
                    self.name,
                    self.location
                )
            else:
                error_msg = u"{0} is required in {1}".format(
                    self.name,
                    " or ".join(self.location)
                )
            self.handle_validation_error(ValueError(error_msg))

        if not results:
            return self.default

        if self.action == "append":
            if (self.max_count and len(results) > self.max_count) or \
               (self.min_count and len(results) < self.min_count):
                self.handle_validation_error(
                    ValueError(
                        'array length out of limit: {} - {}'
                        .format(self.max_count, self.min_count)
                    )
                )
            return results

        if self.action == "restore" or len(results) == 1:
            return results[0]

        return results


class RequestParser(object):
    def __init__(self, argument_class=Argument, namespace_class=NameSpace):
        self.args = []
        self.argument_class = argument_class
        self.namespace_class = namespace_class

    def add_argument(self, *args, **kwargs):
        self.args.append(self.argument_class(*args, **kwargs))
        return self

    def parse_args(self, req, clear_none=False):
        namespace = self.namespace_class()

        for arg in self.args:
            try:
                value = arg.parse(req)
            except ArgumentError as e:
                self.handle_argument_error(e)
            if (value is not None) or (not clear_none):
                namespace[arg.dest or arg.name] = value

        return namespace

    def handle_argument_error(self, e):
        """ 这里可以重写来自定义处理方式 """
        raise BadRequest(unicode(e))

    # some specified arg types
    ###########################################################################
    def add_taglist_argument(self, name, taglength, tagcount, **kwargs):
        return self.add_argument(name, min_len=1, max_len=taglength,
                                 max_count=tagcount, action="append",
                                 operators=("=", "[]"), **kwargs)

    def add_timestamp_argument(self, name, mintime=None, maxtime=None,
                               tolocal=False, **kwargs):
        t = TimestampParse(mintime=mintime, maxtime=maxtime, tolocal=tolocal)
        kwargs["type"] = t
        return self.add_argument(name, **kwargs)

    def add_position_argument(self, name, need_desc=True, **kwargs):
        t = PositionParse(need_desc)
        kwargs["type"] = t
        return self.add_argument(name, **kwargs)

    def add_bool_argument(self, name, **kwargs):
        def parse_bool(value, name):
            value = value.strip().lower()
            if value not in ("true", "false"):
                raise ValueError("value should be 'true'|'false'")
            return value == "true"

        kwargs["type"] = parse_bool
        return self.add_argument(name, **kwargs)

    def add_phone_argument(self, name, **kwargs):
        def check_phone(value, name):
            value = value.strip()
            if not value:
                return None

            try:
                int(value)
            except:
                raise ValueError("phone number invalid")

            if not len(value) == 11:
                raise ValueError("phone number length invalid")

            return value

        kwargs.setdefault("type", check_phone)
        return self.add_argument(name, **kwargs)

    def add_regex_argument(self, name, regex, flags=0, **kwargs):
        t = RegExpParse(regex, flags)
        kwargs["type"] = t
        return self.add_argument(name, **kwargs)

    def add_email_argument(self, name, **kwargs):
        return self.add_regex_argument(name, r'^.+@[^.].*\.[a-z]{2,10}$',
                                       re.IGNORECASE, **kwargs)


# Some types define
###############################################################################
class TimestampParse(object):
    def __init__(self, mintime=None, maxtime=None, tolocal=False):
        self.mintime = mintime
        self.maxtime = maxtime
        self.tolocal = tolocal
        self.dtformat = "%Y-%m-%d %H:%M:%S"
    
    def __call__(self, value, name):
        value = value.strip()
        if not value:
            return None

        try:
            v = int(value)
        except Exception:
            v = int(float(value))
        if self.tolocal:
            dt = datetime.fromtimestamp(v)
        else:
            dt = datetime.utcfromtimestamp(v)

        if self.mintime and dt < self.mintime:
            raise ValueError(
                "datetime ({}) out of limit (mintime={})".format(
                    dt.strftime(self.dtformat),
                    self.mintime.strftime(self.dtformat)
                ))
        if self.maxtime and dt > self.maxtime:
            raise ValueError(
                "datetime ({}) out of limit (maxtime={})".format(
                    dt.strftime(self.dtformat),
                    self.maxtime.strftime(self.dtformat)
                ))

        return dt


class PositionParse(object):
    """ 地址位置参数格式为<mapX:mapY[:description]> """
    def __init__(self, need_desc=True):
        self.need_desc = need_desc

    def __call__(self, value, name):
        value = value.strip()
        if not value:
            return None

        vs = value.split(":", 2)
        mapX, mapY, desc = (vs if len(vs) == 3 else (vs + [None]))
        if self.need_desc and not desc:
            raise ValueError("Position description is needed")

        mapX, mapY = float(mapX), float(mapY)

        pos = NameSpace(x=mapX, y=mapY, desc=desc)

        return pos


class RegExpParse(object):
    """ 正则表达式 """
    def __init__(self, regex, flags=0):
        if isinstance(regex, (str, unicode)):
            regex = re.compile(regex, flags)
        self.regex = regex

    def __call__(self, value, name):
        value = value.strip()
        if not value:
            return None

        if not self.regex.match(value):
            raise ValueError("Can not match regex")

        return value
