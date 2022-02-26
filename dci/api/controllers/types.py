# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import wsme
from wsme import types as wtypes

from oslo_serialization import jsonutils
from oslo_utils import strutils
from oslo_utils import uuidutils

from dci.api.controllers import link
from dci.common import exception
from dci.common.i18n import _


class FilterType(wtypes.UserType):
    """Query filter."""
    name = 'filtertype'
    basetype = wtypes.text

    _supported_fields = wtypes.Enum(wtypes.text, 'limit', 'marker',
                                    'sort_key', 'sort_dir')

    field = wsme.wsattr(_supported_fields, mandatory=True)
    value = wsme.wsattr(wtypes.text, mandatory=True)

    def __repr__(self):
        # for logging calls
        return '<Query %s %s>' % (self.field,
                                  self.value)

    @classmethod
    def sample(cls):
        return cls(field='interface_type',
                   value='pci')

    def as_dict(self):
        d = dict()
        d[getattr(self, 'field')] = getattr(self, 'value')
        return d

    @staticmethod
    def validate(filters):
        for filter in filters:
            if filter.field not in FilterType._supported_fields:
                msg = _("'%s' is an unsupported field for querying.")
                raise wsme.exc.ClientSideError(msg % filter.field)
        return filters


class UUIDType(wtypes.UserType):
    """A simple UUID type."""

    basetype = wtypes.text
    name = 'uuid'

    @staticmethod
    def validate(value):
        if not uuidutils.is_uuid_like(value):
            raise exception.InvalidUUID(uuid=value)
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return UUIDType.validate(value)


class JsonType(wtypes.UserType):
    """A simple JSON type."""

    basetype = wtypes.text
    name = 'json'

    @staticmethod
    def validate(value):
        try:
            jsonutils.dumps(value)
        except TypeError:
            raise exception.InvalidJsonType(value=value)
        else:
            return value

    @staticmethod
    def frombasetype(value):
        return JsonType.validate(value)


class BooleanType(wtypes.UserType):
    """A simple boolean type."""

    basetype = wtypes.text
    name = 'boolean'

    @staticmethod
    def validate(value):
        try:
            return strutils.bool_from_string(value, strict=True)
        except ValueError as e:
            # raise Invalid to return 400 (BadRequest) in the API
            raise exception.Invalid(e)

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


class ListType(wtypes.UserType):
    """A simple list of string type."""

    basetype = wtypes.text
    name = 'list_of_string'

    @staticmethod
    def validate(value):
        try:
            if not isinstance(value, list):
                err_msg = "[%s] not a list type" % value
                raise ValueError(err_msg)
            return value
        except ValueError as e:
            # raise Invalid to return 400 (BadRequest) in the API
            raise exception.Invalid(e)

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return ListType.validate(value)


uuid = UUIDType()
jsontype = JsonType()
boolean = BooleanType()
integer = wtypes.IntegerType()
ipv4 = wtypes.IPv4AddressType()
text = wtypes.text
unset = wtypes.Unset
links = wsme.wsattr([link.Link], readonly=True)
list_of_string = list_of_dict = ListType()
