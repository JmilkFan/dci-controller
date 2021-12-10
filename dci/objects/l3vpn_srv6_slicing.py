from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from dci.common import constants
from dci.db import api as dbapi
from dci.objects import base
from dci.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.DCIObjectRegistry.register
class L3VPNSRv6Slicing(base.DCIObject, object_base.VersionedObjectDictCompat):

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
        'routing_type': object_fields.EnumField(
            valid_values=[constants.BEST_EFFORT,
                          constants.TRAFFIC_ENGINEERING],
            nullable=False),
        'ingress_node': object_fields.StringField(nullable=True),
        'egress_node': object_fields.StringField(nullable=True),
        'route_target': object_fields.StringField(nullable=True),
        'is_keepalive': object_fields.BooleanField(nullable=True),
        'state': object_fields.EnumField(
            valid_values=[constants.ACTIVE,
                          constants.INACTIVE],
            nullable=False)
    }

    def create(self, context):
        """Create a L3VPN over SRv6 network slicing record in the DB."""
        values = self.obj_get_changes()
        db_l3vpn_srv6_slicing = self.dbapi.l3vpn_srv6_slicing_create(context,
                                                                     values)
        self._from_db_object(self, db_l3vpn_srv6_slicing)

    @classmethod
    def get(cls, context, uuid):
        """Find a L3VPN over SRv6 network slicing and return an Obj."""
        db_l3vpn_srv6_slicing = cls.dbapi.l3vpn_srv6_slicing_get(context, uuid)
        obj_l3vpn_srv6_slicing = cls._from_db_object(cls(context),
                                                     db_l3vpn_srv6_slicing)
        return obj_l3vpn_srv6_slicing

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of L3VPN over SRv6 network slicing objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)

            db_l3vpn_srv6_slicings = \
                cls.dbapi.l3vpn_srv6_slicing_list_by_filters(
                    context, filters, sort_dir=sort_dir, sort_key=sort_key,
                    limit=limit, marker=marker)

        else:
            db_l3vpn_srv6_slicings = cls.dbapi.l3vpn_srv6_slicing_list(context)

        return cls._from_db_object_list(db_l3vpn_srv6_slicings, context)

    def save(self, context):
        """Update a L3VPN over SRv6 network slicing record in the DB."""
        updates = self.obj_get_changes()
        db_l3vpn_srv6_slicing = self.dbapi.l3vpn_srv6_slicing_update(context, self.uuid, updates)  # noqa
        self._from_db_object(self, db_l3vpn_srv6_slicing)

    def destroy(self, context):
        """Delete the L3VPN over SRv6 network slicing from the DB."""
        self.dbapi.l3vpn_srv6_slicing_delete(context, self.uuid)
        self.obj_reset_changes()
