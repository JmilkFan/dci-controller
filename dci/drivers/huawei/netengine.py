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

"""
Driver for HUAWEI NetEngine.
"""

import jinja2
import os

from oslo_log import log

from dci.common.i18n import _LE
from dci.drivers.base_driver import DeviceDriver
from dci.drivers.huawei.netconflib import HuaweiNETCONFLib

LOG = log.getLogger(__name__)


class NetEngineDriver(DeviceDriver):
    """Executes commands relating to HUAWEI NetEngine Driver."""

    def __init__(self, host, port, username, password, *args, **kwargs):
        super(NetEngineDriver, self).__init__(*args, **kwargs)

        self.netconf_cli = HuaweiNETCONFLib(host, port, username, password)

    def _get_rpc_command_from_template_file(self, file_name, kwargs={}):
        """Get RPC Command from specified template file.

        :return: Bytes of RPC Command can be parser by `lxml.etree.XMLParser`.
        """
        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         'templates/%s' % file_name))

        try:
            template_loader = jinja2.FileSystemLoader(
                searchpath=os.path.dirname(file_path))

            jinja_env = jinja2.Environment(autoescape=True,
                                           loader=template_loader,
                                           trim_blocks=True,
                                           lstrip_blocks=True)

            template = jinja_env.get_template(os.path.basename(file_path))

            return template.render(**kwargs).encode('UTF-8')

        except Exception as err:
            LOG.error(_LE("Failed to get template file content of [%(file)s], "
                          "details %(err)s"),
                      {'file': file_name, 'err': err})
            raise err

    def _send_rpc_command_to_device(self, rpc_command):
        self.netconf_cli.connect()
        result = self.netconf_cli.executor(rpc_command)
        self.netconf_cli.disconnect()
        return result

    def liveness(self):
        file_name = 'device_ping.xml'
        rpc_command = self._get_rpc_command_from_template_file(file_name)
        self._send_rpc_command_to_device(rpc_command)

    def create_vpls_over_srv6_be_l2vpn(self):
        pass

    def test_netconf(self):
        file_name = 'test.xml'
        rpc_command = self._get_rpc_command_from_template_file(file_name)
        return self._send_rpc_command_to_device(rpc_command)
