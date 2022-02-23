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

    # wan_nodes
    @abc.abstractmethod
    def wan_node_create(self, context, values):
        """Create a new WAN node."""

    @abc.abstractmethod
    def wan_node_get(self, context, uuid):
        """Get a WAN node."""

    @abc.abstractmethod
    def wan_node_list(self, context):
        """Get all WAN node."""

    @abc.abstractmethod
    def wan_node_update(self, context, uuid, values):
        """update a WAN node."""

    @abc.abstractmethod
    def wan_node_delete(self, context, uuid):
        """delete a WAN node."""

    # evpn_vpls_over_srv6_be_slicings
    @abc.abstractmethod
    def evpn_vpls_over_srv6_be_slicing_create(self, context, values):
        """Create a new EVPN VPLS over SRv6 BE network slicing."""

    @abc.abstractmethod
    def evpn_vpls_over_srv6_be_slicing_get(self, context, uuid):
        """Get a EVPN VPLS over SRv6 BE network slicing."""

    @abc.abstractmethod
    def evpn_vpls_over_srv6_be_slicing_list(self, context):
        """Get all EVPN VPLS over SRv6 BE network slicing."""

    @abc.abstractmethod
    def evpn_vpls_over_srv6_be_slicing_update(self, context, uuid, values):
        """update a EVPN VPLS over SRv6 BE network slicing."""

    @abc.abstractmethod
    def evpn_vpls_over_srv6_be_slicing_delete(self, context, uuid):
        """delete a WAN node."""
