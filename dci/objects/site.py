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
from dci.objects.wan_node import WANNode


LOG = logging.getLogger(__name__)


@base.DCIObjectRegistry.register
class Site(base.DCIObject, object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=True),
        'tf_api_server_host': object_fields.StringField(nullable=False),
        'tf_api_server_port': object_fields.IntegerField(nullable=False),
        'tf_username': object_fields.StringField(nullable=False),
        'tf_password': object_fields.StringField(nullable=False),
        'os_auth_url': object_fields.StringField(nullable=True),
        'os_region': object_fields.StringField(nullable=True),
        'os_project_domain_name': object_fields.StringField(nullable=True),
        'os_user_domain_name': object_fields.StringField(nullable=True),
        'os_project_name': object_fields.StringField(nullable=True),
        'os_username': object_fields.StringField(nullable=True),
        'os_password': object_fields.StringField(nullable=True),
        'state': object_fields.EnumField(valid_values=[constants.ACTIVE,
                                                       constants.INACTIVE],
                                         nullable=False),
        'wan_nodes': object_fields.ListOfObjectsField('WANNode',
                                                      nullable=False)
    }

    def as_dict(self):
        dict_ = {}
        for field in self.fields:

            if self.obj_attr_is_set(field):
                if isinstance(getattr(self, field), Site):
                    value = getattr(self, field).as_dict()

                elif field == 'wan_nodes':
                    wan_node_list_of_dict = []
                    wan_nodes = getattr(self, field)
                    for wan_node in wan_nodes:
                        if isinstance(wan_node, WANNode):
                            wan_node_dict = wan_node.as_dict()
                            wan_node_dict.pop('created_at')
                            wan_node_dict.pop('updated_at')
                            wan_node_list_of_dict.append(wan_node_dict)
                    value = wan_node_list_of_dict

                else:
                    value = getattr(self, field)

            dict_[field] = value
        return dict_

    @staticmethod
    def _from_db_object(obj_site, db_site, context):
        for key, field in obj_site.fields.items():

            if key == 'wan_nodes':
                obj_site.wan_nodes = []
                for db_wan_node in db_site.get('wan_nodes'):
                    obj_wan_node = WANNode(context)
                    WANNode._from_db_object(obj_wan_node, db_wan_node)
                    obj_site.wan_nodes.append(obj_wan_node)
            else:
                obj_site[key] = db_site.get(key)

        obj_site.obj_reset_changes()
        return obj_site

    def create(self, context):
        """Create a DCI site record in the DB."""
        values = self.obj_get_changes()
        db_site = self.dbapi.site_create(context, values)
        self._from_db_object(self, db_site, context)

    @classmethod
    def get(cls, context, uuid):
        """Find a DCI site and return an Obj DCI site."""
        db_site = cls.dbapi.site_get(context, uuid)
        obj_site = cls._from_db_object(cls(context), db_site, context)
        return obj_site

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of DCI site objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)
            db_sites = cls.dbapi.site_list_by_filters(
                context, filters, sort_dir=sort_dir, sort_key=sort_key,
                limit=limit, marker=marker)
        else:
            db_sites = cls.dbapi.site_list(context)
        return cls._from_db_object_list(db_sites, context)

    def save(self, context):
        """Update a DCI site record in the DB."""
        updates = self.obj_get_changes()
        db_site = self.dbapi.site_update(context, self.uuid, updates)
        self._from_db_object(self, db_site, context)

    def destroy(self, context):
        """Delete the DCI site from the DB."""
        self.dbapi.site_delete(context, self.uuid)
        self.obj_reset_changes()
