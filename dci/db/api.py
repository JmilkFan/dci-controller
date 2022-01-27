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

    # l2evpn_dcis
    @abc.abstractmethod
    def l2evpn_dci_create(self, context, values):
        """Create a new L2 EVPN DCI."""

    @abc.abstractmethod
    def l2evpn_dci_get(self, context, uuid):
        """Get a L2 EVPN DCI."""

    @abc.abstractmethod
    def l2evpn_dci_list(self, context):
        """Get all L2 EVPN DCI."""

    @abc.abstractmethod
    def l2evpn_dci_update(self, context, uuid, values):
        """update a L2 EVPN DCI."""

    @abc.abstractmethod
    def l2evpn_dci_delete(self, context, uuid):
        """delete a L2 EVPN DCI."""
