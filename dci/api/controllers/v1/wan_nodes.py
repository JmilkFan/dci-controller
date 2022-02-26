# Copyright © 2012 New Dream Network, LLC (DreamHost)
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

from http import HTTPStatus
import pecan

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common import constants
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.device_manager import api as manager_api
from dci import objects


LOG = log.getLogger(__name__)


class WANNode(base.APIBase):
    """API representation of a WAN node.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the WAN node."""

    name = types.text
    """The name of WAN node."""

    vendor = types.text
    """Network Device Vendor."""

    netconf_host = types.ipv4
    """The NETCONF host IP address."""

    netconf_port = types.integer
    """The NETCONF host Port."""

    netconf_username = types.text
    """The NETCONF user."""

    netconf_password = types.text
    """The NETCONF password."""

    as_number = types.integer
    """AS Number."""

    roles = types.list_of_string
    """Roles of WAN Node."""

    site_uuid = types.text
    """UUID of site."""

    state = types.text
    """State of WANNode."""

    preset_evpn_vpls_o_srv6_be_locator_arg = types.text
    """EVPN VPLS over SRv6 BE Locator Arg."""

    preset_evpn_vpls_o_srv6_be_locator = types.text
    """EVPN VPLS over SRv6 BE Locator."""

    preset_evpn_vxlan_nve_intf = types.text
    """EVPN VxLAN NVE Interface."""

    preset_evpn_vxlan_nve_intf_ipaddr = types.ipv4
    """EVPN VxLAN NVE Interface IP address."""

    preset_evpn_vxlan_nve_peer_ipaddr = types.ipv4
    """EVPN VxLAN NVE Peer IP address."""

    preset_wan_vpn_bd_intf = types.text
    """WAN VPN Bridge Domain Interface."""

    preset_access_vpn_bd_intf = types.text
    """Access VPN Bridge Domain Interface."""

    links = types.links
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(WANNode, self).__init__(**kwargs)
        self.fields = []
        for field in objects.WANNode.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, types.unset))

    @classmethod
    def convert_with_links(cls, obj_wan_node):
        api_wan_node = cls(**obj_wan_node.as_dict())
        api_wan_node.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'wan_nodes', api_wan_node.uuid)
            ]
        return api_wan_node


class WANNodeCollection(base.APIBase):
    """API representation of a collection of WAN nodes."""

    wan_nodes = [WANNode]
    """A list containing WANNode objects"""

    @classmethod
    def convert_with_links(cls, wan_nodes):
        collection = cls()
        collection.wan_nodes = [WANNode.convert_with_links(wan_node)
                                for wan_node in wan_nodes]
        return collection


class WANNodeController(base.DCIController):
    """REST controller for WAN node Controller.
    """

    @expose.expose(WANNode, types.text)
    def get_one(self, uuid):
        """Get a single WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        LOG.info(_LI("[wan_nodes: get_one] UUID = (%s)"), uuid)
        context = pecan.request.context
        obj_wan_node = objects.WANNode.get(context, uuid)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNodeCollection, types.text)
    def get_all(self, state=None):
        """Retrieve a list of WANNode.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state

        LOG.info(_LI('[wan_nodes: get_all] filters = %s'), filters_dict)
        context = pecan.request.context
        obj_wan_nodes = objects.WANNode.list(context, filters=filters_dict)
        return WANNodeCollection.convert_with_links(obj_wan_nodes)

    @expose.expose(WANNode, body=WANNode,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one WANNode.
        """
        req_body = req_body.as_dict()
        LOG.info(_LI("[wan_nodes: port] Request body = %s"), req_body)
        context = pecan.request.context

        vendor = req_body.get('vendor')
        if vendor not in constants.LIST_OF_VAILD_DEVICE_VENDOR:
            msg = _LE("Invalid device vendor %(vendor)s, the optional "
                      "vendor are %(list)s.") % {
                          'vendor': vendor,
                          'list': constants.LIST_OF_VAILD_DEVICE_VENDOR}
            LOG.error(msg)
            raise exception.InvalidRequestBody(msg)

        if req_body.get('roles') \
                and constants.WAN_NODE_ROLE_DCGW in req_body.get('roles'):
            site_uuid = req_body['site_uuid']
            try:
                objects.Site.get(context, site_uuid)
            except exception.ResourceNotFound as err:
                raise err
            except Exception as err:
                raise err

        dev_manager = manager_api.DeviceManager(device_conn_ref=req_body)
        dev_manager.device_ping()

        req_body['state'] = constants.ACTIVE
        obj_wan_node = objects.WANNode(context, **req_body)
        obj_wan_node.create(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNode, types.text, body=WANNode,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a WANNode.
        """
        req_body = req_body.as_dict()
        LOG.info("[wan_nodes: put] Request body = %s", req_body)
        context = pecan.request.context

        obj_wan_node = objects.WANNode.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_wan_node, k) != v:
                setattr(obj_wan_node, k, v)

        obj_wan_node.save(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(None, types.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        context = pecan.request.context
        LOG.info('[wan_node: delete] UUID = (%s)', uuid)
        obj_wan_node = objects.WANNode.get(context, uuid)
        obj_wan_node.destroy(context)
