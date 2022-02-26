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
from dci.device_manager.base_driver import DeviceDriver
from dci.device_manager.drivers.huawei import netconflib

LOG = log.getLogger(__name__)


class NetEngineDriver(DeviceDriver):
    """Executes commands relating to HUAWEI NetEngine Driver."""

    def __init__(self, host, port, username, password, *args, **kwargs):
        super(NetEngineDriver, self).__init__(*args, **kwargs)

        self.netconf_cli = netconflib.HuaweiNETCONFLib(
            host, port, username, password)

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

    def test_netconf(self):
        file_name = 'test.xml'
        rpc_command = self._get_rpc_command_from_template_file(file_name)
        return self._send_rpc_command_to_device(rpc_command)

    def create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self, wan_vpn_name, wan_vpn_rd, wan_vpn_rt,
            preset_srv6_locator_arg, preset_srv6_locator_arg_prefix,
            preset_srv6_locator_arg_prefix_len, preset_srv6_locator,
            preset_srv6_locator_prefix, preset_srv6_locator_prefix_len,
            access_vpn_name, access_vpn_rd, access_vpn_rt,
            access_vpn_vxlan_vni, preset_vxlan_nve_intf,
            preset_vxlan_nve_intf_ipaddr, preset_vxlan_nve_peer_ipaddr,
            splicing_vlan_id, wan_vpn_bd, preset_wan_vpn_bd_intf,
            access_vpn_bd, preset_access_vpn_bd_intf,
            *args, **kwargs):
        """Create EVPN VPLS over SRv6 BE WAN VPN and EVPN VxLAN Access VPN at
        the same time.
        """
        file_name = 'create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn.xml'  # noqa
        kwargs = {
            # WAN VPN
            'WAN_VPN_NAME': wan_vpn_name,
            'WAN_VPN_RD': wan_vpn_rd,
            'WAN_VPN_RT': wan_vpn_rt,
            'PRESET_SRV6_LOCATOR_ARG': preset_srv6_locator_arg,
            'PRESET_SRV6_LOCATOR_ARG_PREFIX': preset_srv6_locator_arg_prefix,
            'PRESET_SRV6_LOCATOR_ARG_PREFIX_LEN': preset_srv6_locator_arg_prefix_len,  # noqa
            'PRESET_SRV6_LOCATOR': preset_srv6_locator,
            'PRESET_SRV6_LOCATOR_PREFIX': preset_srv6_locator_prefix,
            'PRESET_SRV6_LOCATOR_PREFIX_LEN': preset_srv6_locator_prefix_len,

            # ACCESS VPN
            'ACCESS_VPN_NAME': access_vpn_name,
            'ACCESS_VPN_RD': access_vpn_rd,
            'ACCESS_VPN_RT': access_vpn_rt,
            'ACCESS_VPN_VXLAN_VNI': access_vpn_vxlan_vni,
            'PRESET_VXLAN_NVE_INTERFACE': preset_vxlan_nve_intf,
            'PRESET_VXLAN_NVE_INTERFACE_IP_ADDRESS': preset_vxlan_nve_intf_ipaddr,  # noqa
            'PRESET_VXLAN_NVE_PEER_IP_ADDRESS': preset_vxlan_nve_peer_ipaddr,

            # VPN Splicing
            'SPLICING_VID': splicing_vlan_id,
            'WAN_VPN_BD': wan_vpn_bd,
            'PRESET_WAN_VPN_BD_INTERFACE': preset_wan_vpn_bd_intf,
            'ACCESS_VPN_BD': access_vpn_bd,
            'PRESET_ACCESS_VPN_BD_INTERFACE': preset_access_vpn_bd_intf
        }
        rpc_command = self._get_rpc_command_from_template_file(file_name,
                                                               kwargs)
        return self._send_rpc_command_to_device(rpc_command)

    def delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self, wan_vpn_name, access_vpn_name, access_vpn_vxlan_vni,
            preset_vxlan_nve_intf, preset_vxlan_nve_intf_ipaddr,
            wan_vpn_bd, preset_wan_vpn_bd_intf, access_vpn_bd,
            preset_access_vpn_bd_intf, *args, **kwargs):
        """Delete EVPN VPLS over SRv6 BE WAN VPN and EVPN VxLAN Access VPN at
        the same time.
        """
        file_name = 'delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn.xml'  # noqa
        kwargs = {
            # WAN VPN
            'WAN_VPN_NAME': wan_vpn_name,

            # ACCESS VPN
            'ACCESS_VPN_NAME': access_vpn_name,
            'ACCESS_VPN_VXLAN_VNI': access_vpn_vxlan_vni,
            'PRESET_VXLAN_NVE_INTERFACE': preset_vxlan_nve_intf,

            # VPN Splicing
            'WAN_VPN_BD': wan_vpn_bd,
            'PRESET_WAN_VPN_BD_INTERFACE': preset_wan_vpn_bd_intf,
            'ACCESS_VPN_BD': access_vpn_bd,
            'PRESET_ACCESS_VPN_BD_INTERFACE': preset_access_vpn_bd_intf
        }
        rpc_command = self._get_rpc_command_from_template_file(file_name,
                                                               kwargs)
        return self._send_rpc_command_to_device(rpc_command)
