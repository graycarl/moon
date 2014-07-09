# -*- coding: utf-8 -*-
from uuid import UUID
from werkzeug.routing import BaseConverter, ValidationError


class UUIDConverter(BaseConverter):
    """ UUID类型，适配如下形式
        1. 1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a
        2. 1a1a1a1a-1a1a-1a1a-1a1a-1a1a1a1a1a1a
    """
    def __init__(self, map, dash=None):
        super(UUIDConverter, self).__init__(map)
        self.dash = dash
        if dash is True:
            self.regex = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}' \
                         r'-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        elif dash is False:
            self.regex = r'[0-9a-fA-F]{32}'
        else:
            self.regex = r'[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}' \
                         r'-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}'

    def to_python(self, value):
        try:
            return UUID(value)
        except:
            raise ValidationError()

    def to_url(self, value):
        return str(value) if self.dash is True else value.hex
