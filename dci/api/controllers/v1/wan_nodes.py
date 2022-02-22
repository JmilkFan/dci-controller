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
import wsme
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common import constants
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci import manager
from dci import objects


LOG = log.getLogger(__name__)


class WANNode(base.APIBase):
    """API representation of a WAN node.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the WAN node."""

    name = wtypes.text
    """The name of WAN node."""

    vendor = wtypes.text
    """Network Device Vendor."""

    netconf_host = wtypes.IPv4AddressType()
    """The NETCONF host IP address."""

    netconf_port = wtypes.IntegerType()
    """The NETCONF host Port."""

    netconf_username = wtypes.text
    """The NETCONF user."""

    netconf_password = wtypes.text
    """The NETCONF password."""

    as_number = wtypes.IntegerType()
    """AS Number."""

    state = wtypes.text
    """State of WANNode."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(WANNode, self).__init__(**kwargs)
        self.fields = []
        for field in objects.WANNode.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

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

    @expose.expose(WANNode, wtypes.text)
    def get_one(self, uuid):
        """Get a single WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        LOG.info(_LI("[wan_nodes: get_one] UUID = (%s)"), uuid)
        context = pecan.request.context
        obj_wan_node = objects.WANNode.get(context, uuid)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNodeCollection, wtypes.text)
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

    @expose.expose(WANNode, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one WANNode.
        """
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

        dev_manager = manager.DeviceManager(device_connection_info=req_body)  # noqa
        dev_manager.device_ping()

        req_body['state'] = constants.ACTIVE
        obj_wan_node = objects.WANNode(context, **req_body)
        obj_wan_node.create(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNode, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a WANNode.
        """
        LOG.info("[wan_nodes: put] Request body = %s", req_body)
        context = pecan.request.context

        obj_wan_node = objects.WANNode.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_wan_node, k) != v:
                setattr(obj_wan_node, k, v)

        obj_wan_node.save(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        context = pecan.request.context
        LOG.info('[wan_node: delete] UUID = (%s)', uuid)
        obj_wan_node = objects.WANNode.get(context, uuid)
        obj_wan_node.destroy(context)
