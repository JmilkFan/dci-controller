from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from dci.db import api as dbapi
from dci.objects import base
from dci.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.DCIObjectRegistry.register
class Site(base.DCIObject, object_base.VersionedObjectDictCompat):

    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=True),
        'netconf_host': object_fields.StringField(nullable=False),
        'netconf_username': object_fields.StringField(nullable=False),
        'netconf_password': object_fields.StringField(nullable=False),
        'state': object_fields.EnumField(valid_values=['active', 'inactive'],
                                         nullable=False)
    }

    def create(self, context):
        """Create a DCI site record in the DB."""
        values = self.obj_get_changes()
        db_site = self.dbapi.site_create(context, values)
        self._from_db_object(self, db_site)

    @classmethod
    def get(cls, context, uuid):
        """Find a DCI site and return an Obj DCI site."""
        db_site = cls.dbapi.site_get(context, uuid)
        obj_site = cls._from_db_object(cls(context), db_site)
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
        self._from_db_object(self, db_site)

    def destroy(self, context):
        """Delete the DCI site from the DB."""
        self.dbapi.site_delete(context, self.uuid)
        self.obj_reset_changes()