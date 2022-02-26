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

from oslo_log import log as logging
from oslo_utils import versionutils
from oslo_versionedobjects import base as object_base

from dci import objects
from dci.objects import fields as object_fields


LOG = logging.getLogger(__name__)


class DCIObjectRegistry(object_base.VersionedObjectRegistry):
    def registration_hook(self, cls, index):

        version = versionutils.convert_version_to_tuple(cls.VERSION)
        if not hasattr(objects, cls.obj_name()):
            setattr(objects, cls.obj_name(), cls)
        else:
            cur_version = versionutils.convert_version_to_tuple(
                getattr(objects, cls.obj_name()).VERSION)
            if version >= cur_version:
                setattr(objects, cls.obj_name(), cls)


class DCIObject(object_base.VersionedObject):
    """Base class and object factory.

    This forms the base of all objects that can be remoted or instantiated
    via RPC. Simply defining a class that inherits from this base class
    will make it remotely instantiatable. Objects should implement the
    necessary "get" classmethod routines as well as "save" object methods
    as appropriate.
    """

    OBJ_SERIAL_NAMESPACE = 'dci_object'
    OBJ_PROJECT_NAMESPACE = 'dci-controller'

    fields = {
        'created_at': object_fields.DateTimeField(nullable=True),
        'updated_at': object_fields.DateTimeField(nullable=True),
    }

    def as_dict(self):
        """Return the object represented as a dict.

        The returned object is JSON-serialisable.
        """

        def _attr_as_dict(field):
            """Return an attribute as a dict, handling nested objects."""

            attr = getattr(self, field)
            if isinstance(attr, DCIObject):
                attr = attr.as_dict()
            return attr

        return {k: _attr_as_dict(k)
                for k in self.fields if self.obj_attr_is_set(k)}

    @staticmethod
    def _from_db_object(obj, db_obj, context=None):
        """Converts a database entity to a formal object.

        :param obj: An object of the class.
        :param db_obj: A DB model of the object
        :return: The object of the class with the database entity added
        """

        for field in obj.fields:
            obj[field] = db_obj[field]

        obj.obj_reset_changes()
        return obj

    @classmethod
    def _from_db_object_list(cls, db_objs, context):
        """Converts a list of database entities to a list of formal objects."""

        objs = []
        for db_obj in db_objs:
            objs.append(cls._from_db_object(cls(context), db_obj, context))
        return objs

    def obj_make_compatible(self, primitive, target_version):
        """Make an object representation compatible with a target version.

        This is responsible for taking the primitive representation of
        an object and making it suitable for the given target_version.
        This may mean converting the format of object attributes, removing
        attributes that have been added since the target version, etc.

        :param:primitive: The result of self.obj_to_primitive()
        :param:target_version: The version string requested by the recipient
                               of the object.
        """
        _log_backport(self, target_version)
        super(DCIObject, self).obj_make_compatible(primitive,
                                                   target_version)


def _log_backport(ovo, target_version):
    """Log backported versioned objects."""
    if target_version and target_version != ovo.VERSION:
        LOG.debug('Backporting %(obj_name)s from version %(src_vers)s '
                  'to version %(dst_vers)s',
                  {'obj_name': ovo.obj_name(),
                   'src_vers': ovo.VERSION,
                   'dst_vers': target_version})
