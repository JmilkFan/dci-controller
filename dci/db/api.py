import abc

from oslo_config import cfg
from oslo_db import api as db_api


_BACKEND_MAPPING = {'sqlalchemy': 'dci.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


class Connection(object, metaclass=abc.ABCMeta):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    # sites
    @abc.abstractmethod
    def site_create(self, context, values):
        """Create a new DCI site."""

    @abc.abstractmethod
    def site_get(self, context, uuid):
        """Get a DCI site."""

    @abc.abstractmethod
    def site_list(self, context):
        """Get all DCI site."""

    @abc.abstractmethod
    def site_update(self, context, uuid, values):
        """update a DCI site."""

    @abc.abstractmethod
    def site_delete(self, context, uuid):
        """delete a DCI site."""

    # l3evpn_dcis
    @abc.abstractmethod
    def l3evpn_dci_create(self, context, values):
        """Create a new L3 EVPN DCI."""

    @abc.abstractmethod
    def l3evpn_dci_get(self, context, uuid):
        """Get a L3 EVPN DCI."""

    @abc.abstractmethod
    def l3evpn_dci_list(self, context):
        """Get all L3 EVPN DCI."""

    @abc.abstractmethod
    def l3evpn_dci_update(self, context, uuid, values):
        """update a L3 EVPN DCI."""

    @abc.abstractmethod
    def l3evpn_dci_delete(self, context, uuid):
        """delete a L3 EVPN DCI."""
