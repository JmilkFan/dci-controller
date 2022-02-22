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
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import types
from dci.api import expose
from dci.common.i18n import _LI
from dci.manager import DeviceManager
from dci import objects


LOG = log.getLogger(__name__)


class TestController(base.DCIController):
    """REST controller for Test NETCONF Controller.
    """

    @expose.expose(wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one WANNode.
        """
        LOG.info(_LI("[test_netconf: port] Request body = %s"), req_body)
        context = pecan.request.context

        wan_node_uuid = req_body.get('wan_node_uuid')
        obj_wan_node = objects.WANNode.get(context, wan_node_uuid)

        device_connection_info = {
            'vendor': obj_wan_node.vendor,
            'netconf_host': obj_wan_node.netconf_host,
            'netconf_port': obj_wan_node.netconf_port,
            'netconf_username': obj_wan_node.netconf_username,
            'netconf_password': obj_wan_node.netconf_password
        }

        wan_manager = DeviceManager(device_connection_info)
        return wan_manager.test_netconf()
