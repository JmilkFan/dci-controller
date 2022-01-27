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
class WANNode(base.DCIObject, object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=True),
        'vendor': object_fields.EnumField(
            valid_values=[constants.HUAWEI], nullable=False),
        'configure_mode': object_fields.EnumField(
            valid_values=[constants.SSHCLI, constants.NETCONF],
            nullable=False),
        'ssh_host': object_fields.StringField(nullable=False),
        'ssh_port': object_fields.IntegerField(nullable=False),
        'ssh_username': object_fields.StringField(nullable=False),
        'ssh_password': object_fields.StringField(nullable=False),
        'privilege_password': object_fields.StringField(nullable=False),
        'as_number': object_fields.IntegerField(nullable=True),
        'state': object_fields.EnumField(
            valid_values=[constants.ACTIVE, constants.INACTIVE],
            nullable=False)
    }

    def create(self, context):
        """Create a WAN node record in the DB."""
        values = self.obj_get_changes()
        db_wan_node = self.dbapi.wan_node_create(context, values)
        self._from_db_object(self, db_wan_node)

    @classmethod
    def get(cls, context, uuid):
        """Find a WAN node and return an Obj WAN node."""
        db_wan_node = cls.dbapi.wan_node_get(context, uuid)
        obj_wan_node = cls._from_db_object(cls(context), db_wan_node)
        return obj_wan_node

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of WAN node objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)
            db_wan_nodes = cls.dbapi.wan_node_list_by_filters(
                context, filters, sort_dir=sort_dir, sort_key=sort_key,
                limit=limit, marker=marker)
        else:
            db_wan_nodes = cls.dbapi.wan_node_list(context)
        return cls._from_db_object_list(db_wan_nodes, context)

    def save(self, context):
        """Update a WAN node record in the DB."""
        updates = self.obj_get_changes()
        db_wan_node = self.dbapi.wan_node_update(context, self.uuid, updates)
        self._from_db_object(self, db_wan_node)

    def destroy(self, context):
        """Delete the WAN node from the DB."""
        self.dbapi.wan_node_delete(context, self.uuid)
        self.obj_reset_changes()
