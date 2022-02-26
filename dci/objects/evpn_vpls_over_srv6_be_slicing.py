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
class EVPNVPLSoSRv6BESlicing(base.DCIObject,
                             object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=False),
        'subnet_cidr': object_fields.StringField(nullable=False),
        'state': object_fields.EnumField(valid_values=[constants.ACTIVE,
                                                       constants.INACTIVE],
                                         nullable=False),

        'east_site_uuid': object_fields.UUIDField(nullable=False),
        'east_dcn_vn_uuid': object_fields.UUIDField(nullable=False),
        'east_dcn_vn_vni': object_fields.StringField(nullable=False),
        'east_dcn_vn_route_target': object_fields.StringField(nullable=False),
        'east_dcn_vn_subnet_allocation_pool': object_fields.StringField(nullable=False),  # noqa
        'east_access_vpn_vni': object_fields.StringField(nullable=False),
        'east_access_vpn_route_target': object_fields.StringField(nullable=False),  # noqa
        'east_access_vpn_route_distinguisher': object_fields.StringField(nullable=False),  # noqa
        'east_wan_vpn_route_target': object_fields.StringField(nullable=False),  # noqa
        'east_wan_vpn_route_distinguisher': object_fields.StringField(nullable=False),  # noqa
        'east_access_vpn_bridge_domain': object_fields.StringField(nullable=False),  # noqa
        'east_wan_vpn_bridge_domain': object_fields.StringField(nullable=False),  # noqa
        'east_splicing_vlan_id': object_fields.StringField(nullable=False),

        'west_site_uuid': object_fields.UUIDField(nullable=False),
        'west_dcn_vn_uuid': object_fields.UUIDField(nullable=False),
        'west_dcn_vn_vni': object_fields.StringField(nullable=False),
        'west_dcn_vn_route_target': object_fields.StringField(nullable=False),
        'west_dcn_vn_subnet_allocation_pool': object_fields.StringField(nullable=False),  # noqa
        'west_access_vpn_vni': object_fields.StringField(nullable=False),
        'west_access_vpn_route_target': object_fields.StringField(nullable=False),  # noqa
        'west_access_vpn_route_distinguisher': object_fields.StringField(nullable=False),  # noqa
        'west_wan_vpn_route_target': object_fields.StringField(nullable=False),  # noqa
        'west_wan_vpn_route_distinguisher': object_fields.StringField(nullable=False),  # noqa
        'west_access_vpn_bridge_domain': object_fields.StringField(nullable=False),  # noqa
        'west_wan_vpn_bridge_domain': object_fields.StringField(nullable=False),  # noqa
        'west_splicing_vlan_id': object_fields.StringField(nullable=False),
    }

    def create(self, context):
        """Create a EVPN VPLS over SRv6 BE network slicing record in the DB."""
        values = self.obj_get_changes()
        db_evpn_vpls_over_srv6_be_slicing = \
            self.dbapi.evpn_vpls_over_srv6_be_slicing_create(context, values)
        self._from_db_object(self, db_evpn_vpls_over_srv6_be_slicing)

    @classmethod
    def get(cls, context, uuid):
        """Find a EVPN VPLS over SRv6 BE network slicing and return an Obj."""
        db_evpn_vpls_over_srv6_be_slicing = \
            cls.dbapi.evpn_vpls_over_srv6_be_slicing_get(context, uuid)
        obj_evpn_vpls_over_srv6_be_slicing = \
            cls._from_db_object(cls(context),
                                db_evpn_vpls_over_srv6_be_slicing)
        return obj_evpn_vpls_over_srv6_be_slicing

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of EVPN VPLS over SRv6 BE network slicing objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)

            db_evpn_vpls_over_srv6_be_slicings = \
                cls.dbapi.evpn_vpls_over_srv6_be_slicing_list_by_filters(
                    context, filters, sort_dir=sort_dir, sort_key=sort_key,
                    limit=limit, marker=marker)

        else:
            db_evpn_vpls_over_srv6_be_slicings = \
                cls.dbapi.evpn_vpls_over_srv6_be_slicing_list(context)

        return cls._from_db_object_list(db_evpn_vpls_over_srv6_be_slicings,
                                        context)

    def save(self, context):
        """Update a EVPN VPLS over SRv6 BE network slicing record in the DB."""
        updates = self.obj_get_changes()
        db_evpn_vpls_over_srv6_be_slicing = \
            self.dbapi.evpn_vpls_over_srv6_be_slicing_update(
                context, self.uuid, updates)
        self._from_db_object(self, db_evpn_vpls_over_srv6_be_slicing)

    def destroy(self, context):
        """Delete the EVPN VPLS over SRv6 BE network slicing from the DB."""
        self.dbapi.evpn_vpls_over_srv6_be_slicing_delete(context, self.uuid)
        self.obj_reset_changes()
