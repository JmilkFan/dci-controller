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

from dci.common import constants
from dci.device_manager.drivers.huawei import netengine
from dci.sdnc_manager.tungsten_fabric import vnc_api_client as tf_vnc_api


class NetworkSlicingManager(object):

    def __init__(self, obj_east_site, obj_west_site, slicing_name):
        self.obj_east_wan_node = obj_east_site.wan_nodes[0]
        self.east_sdnc_mgr = self._get_sdnc_mgr(obj_east_site)
        self.east_dev_mgr = self._get_dev_mgr(self.obj_east_wan_node)

        self.obj_west_wan_node = obj_west_site.wan_nodes[0]
        self.west_sdnc_mgr = self._get_sdnc_mgr(obj_west_site)
        self.west_dev_mgr = self._get_dev_mgr(self.obj_west_wan_node)

        self.vn_name = constants.VN_NAME_PREFIX + slicing_name
        self.wan_vpn_name = constants.WAN_VPN_NAME_PREFIX + slicing_name
        self.access_vpn_name = constants.ACCESS_VPN_NAME_PREFIX + slicing_name

    def _get_sdnc_mgr(self, site):
        return tf_vnc_api.Client(
            host=site.tf_api_server_host,
            port=site.tf_api_server_port,
            username=site.tf_username,
            password=site.tf_password,
            project=site.os_project_name)

    def _get_dev_mgr(self, wan_node):
        return netengine.NetEngineDriver(
            host=wan_node.netconf_host,
            port=wan_node.netconf_port,
            username=wan_node.netconf_username,
            password=wan_node.netconf_password)

    def create_evpn_vxlan_dcn(self, sdnc_mgr, subnet_cidr,
                              subnet_allocation_pool, route_target):
        route_target = 'target:%s' % route_target
        vn_uuid = sdnc_mgr.create_virtal_network_with_user_defined_subnet(
            self.vn_name, subnet_cidr, subnet_allocation_pool, route_target)
        return vn_uuid

    def get_evpn_vxlan_dcn_vni(self, sdnc_mgr, vn_uuid):
        return sdnc_mgr.get_virtual_network_vni(vn_uuid)

    def delete_evpn_vxlan_dcn(self, sdnc_mgr):
        sdnc_mgr.delete_virtual_network(self.vn_name)

    def create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self, dev_mgr, wan_node,
            wan_vpn_rd, wan_vpn_rt, wan_vpn_bd,
            access_vpn_rd, access_vpn_rt, access_vpn_bd,
            access_vpn_vxlan_vni, splicing_vlan_id):
        dev_mgr.create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            wan_vpn_name=self.wan_vpn_name,
            wan_vpn_rd=wan_vpn_rd,
            wan_vpn_rt=wan_vpn_rt,
            preset_srv6_locator_arg=wan_node.preset_evpn_vpls_o_srv6_be_locator_arg,  # noqa
            preset_srv6_locator=wan_node.preset_evpn_vpls_o_srv6_be_locator,
            access_vpn_name=self.access_vpn_name,
            access_vpn_rd=access_vpn_rd,
            access_vpn_rt=access_vpn_rt,
            access_vpn_vxlan_vni=access_vpn_vxlan_vni,
            preset_vxlan_nve_intf=wan_node.preset_evpn_vxlan_nve_intf,
            preset_vxlan_nve_intf_ipaddr=wan_node.preset_evpn_vxlan_nve_intf_ipaddr,  # noqa
            preset_vxlan_nve_peer_ipaddr=wan_node.preset_evpn_vxlan_nve_peer_ipaddr,  # noqa
            splicing_vlan_id=splicing_vlan_id,
            wan_vpn_bd=wan_vpn_bd,
            preset_wan_vpn_bd_intf=wan_node.preset_wan_vpn_bd_intf,
            access_vpn_bd=access_vpn_bd,
            preset_access_vpn_bd_intf=wan_node.preset_access_vpn_bd_intf
        )

    def delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self, dev_mgr, wan_node, access_vpn_vxlan_vni,
            wan_vpn_bd, access_vpn_bd):
        dev_mgr.delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            wan_vpn_name=self.wan_vpn_name,
            access_vpn_name=self.access_vpn_name,
            access_vpn_vxlan_vni=access_vpn_vxlan_vni,
            preset_vxlan_nve_intf=wan_node.preset_evpn_vxlan_nve_intf,
            preset_vxlan_nve_intf_ipaddr=wan_node.preset_evpn_vxlan_nve_intf_ipaddr,  # noqa
            wan_vpn_bd=wan_vpn_bd,
            preset_wan_vpn_bd_intf=wan_node.preset_wan_vpn_bd_intf,
            access_vpn_bd=access_vpn_bd,
            preset_access_vpn_bd_intf=wan_node.preset_access_vpn_bd_intf
        )
