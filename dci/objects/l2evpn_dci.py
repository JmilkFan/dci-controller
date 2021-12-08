from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from dci.db import api as dbapi
from dci.objects import base
from dci.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.DCIObjectRegistry.register
class L2EVPNDCI(base.DCIObject, object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=True),
        'east_site_uuid': object_fields.UUIDField(nullable=False),
        'west_site_uuid': object_fields.UUIDField(nullable=False),
        'subnet_cidr': object_fields.StringField(nullable=False),
        'east_site_subnet_allocation_pool': object_fields.StringField(nullable=False),  # noqa
        'west_site_subnet_allocation_pool': object_fields.StringField(nullable=False),  # noqa
        'vn_route_target': object_fields.StringField(nullable=False),
        'inter_vlan_id': object_fields.IntegerField(nullable=False),
        'dci_vni': object_fields.IntegerField(nullable=False),
        'east_site_vn_uuid': object_fields.StringField(nullable=True),
        'west_site_vn_uuid': object_fields.StringField(nullable=True),
        'state': object_fields.EnumField(valid_values=['active', 'inactive'],
                                         nullable=False)
    }

    def create(self, context):
        """Create a L2 EVPN DCI record in the DB."""
        values = self.obj_get_changes()
        db_l2evpn_dci = self.dbapi.l2evpn_dci_create(context, values)
        self._from_db_object(self, db_l2evpn_dci)

    @classmethod
    def get(cls, context, uuid):
        """Find a L2 EVPN DCI and return an Obj."""
        db_l2evpn_dci = cls.dbapi.l2evpn_dci_get(context, uuid)
        obj_l2evpn_dci = cls._from_db_object(cls(context), db_l2evpn_dci)
        return obj_l2evpn_dci

    @classmethod
    def list(cls, context, filters=None):
        """Return a list of L2 EVPN DCI objects."""
        if filters:
            sort_dir = filters.pop('sort_dir', 'desc')
            sort_key = filters.pop('sort_key', 'created_at')
            limit = filters.pop('limit', None)
            marker = filters.pop('marker_obj', None)

            db_l2evpn_dcis = cls.dbapi.l2evpn_dci_list_by_filters(
                context, filters, sort_dir=sort_dir, sort_key=sort_key,
                limit=limit, marker=marker)

        else:
            db_l2evpn_dcis = cls.dbapi.l2evpn_dci_list(context)

        return cls._from_db_object_list(db_l2evpn_dcis, context)

    def save(self, context):
        """Update a L2 EVPN DCI record in the DB."""
        updates = self.obj_get_changes()
        db_l2evpn_dci = self.dbapi.l2evpn_dci_update(context, self.uuid, updates)  # noqa
        self._from_db_object(self, db_l2evpn_dci)

    def destroy(self, context):
        """Delete the L2 EVPN DCI from the DB."""
        self.dbapi.l2evpn_dci_delete(context, self.uuid)
        self.obj_reset_changes()
