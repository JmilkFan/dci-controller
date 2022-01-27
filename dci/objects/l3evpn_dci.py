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
from oslo_versionedobjects import base as object_base

from dci.common import constants
from dci.db import api as dbapi
from dci.objects import base
from dci.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.DCIObjectRegistry.register
class L3EVPNDCI(base.DCIObject, object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=True),
        'east_site_uuid': object_fields.UUIDField(nullable=False),
        'east_site_subnet_cidr': object_fields.StringField(nullable=True),
        'east_site_vn_uuid': object_fields.StringField(nullable=True),
        'west_site_uuid': object_fields.UUIDField(nullable=False),
        'west_site_subnet_cidr': object_fields.StringField(nullable=True),
        'west_site_vn_uuid': object_fields.StringField(nullable=True),
        'state': object_fields.EnumField(valid_values=[constants.ACTIVE,
                                                       constants.INACTIVE],
                                         nullable=False)
    }

    def create(self, context):
        """Create a L3 EVPN DCI record in the DB."""
        values = self.obj_get_changes()
        db_l3evpn_dci = self.dbapi.l3evpn_dci_create(context, values)
        self._from_db_object(self, db_l3evpn_dci)

    @classmethod
    def get(cls, context, uuid):
        """Find a L3 EVPN DCI and return an Obj."""
        db_l3evpn_dci = cls.dbapi.l3evpn_dci_get(context, uuid)
        obj_l3evpn_dci = cls._from_db_object(cls(context), db_l3evpn_dci)
        return obj_l3evpn_dci

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of L3 EVPN DCI objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)

            db_l3evpn_dcis = cls.dbapi.l3evpn_dci_list_by_filters(
                context, filters, sort_dir=sort_dir, sort_key=sort_key,
                limit=limit, marker=marker)

        else:
            db_l3evpn_dcis = cls.dbapi.l3evpn_dci_list(context)

        return cls._from_db_object_list(db_l3evpn_dcis, context)

    def save(self, context):
        """Update a L3 EVPN DCI record in the DB."""
        updates = self.obj_get_changes()
        db_l3evpn_dci = self.dbapi.l3evpn_dci_update(context, self.uuid, updates)  # noqa
        self._from_db_object(self, db_l3evpn_dci)

    def destroy(self, context):
        """Delete the L3 EVPN DCI from the DB."""
        self.dbapi.l3evpn_dci_delete(context, self.uuid)
        self.obj_reset_changes()
