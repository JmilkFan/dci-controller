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
from dci.common import utils
from dci.device_manager.drivers.huawei import netengine
from dci.sdnc_manager.tungsten_fabric import vnc_api_client as tf_vnc_api
from dci.task_flows import flows
from dci.task_flows import tasks


def _prepare_l2vpn_slicing_configuration():

    # Route Distinguisher
    east_wan_vpn_rd = utils.generate_random_route_distinguisher()
    east_access_vpn_rd = utils.generate_random_route_distinguisher()
    west_wan_vpn_rd = utils.generate_random_route_distinguisher()
    west_access_vpn_rd = utils.generate_random_route_distinguisher()

    # Route Target
    east_vn_rt = east_access_vpn_rt = utils.generate_random_route_target()
    west_vn_rt = west_access_vpn_rt = utils.generate_random_route_target()
    east_wan_vpn_rt = west_wan_vpn_rt = utils.generate_random_route_target()

    # Bridge Domain
    east_wan_vpn_bd = west_wan_vpn_bd = utils.generate_random_bridge_domain()
    east_access_vpn_bd = west_access_vpn_bd = utils.generate_random_bridge_domain()  # noqa

    # VLAN
    splicing_vlan_id = utils.generate_random_vlan_id()

    configuration = {
        'east_wan_vpn_rd': east_wan_vpn_rd,
        'east_wan_vpn_rt': east_wan_vpn_rt,
        'east_wan_vpn_bd': east_wan_vpn_bd,
        'east_access_vpn_rd': east_access_vpn_rd,
        'east_access_vpn_rt': east_access_vpn_rt,
        'east_access_vpn_bd': east_access_vpn_bd,
        'east_vn_rt': east_vn_rt,

        'west_wan_vpn_rd': west_wan_vpn_rd,
        'west_wan_vpn_rt': west_wan_vpn_rt,
        'west_wan_vpn_bd': west_wan_vpn_bd,
        'west_access_vpn_rd': west_access_vpn_rd,
        'west_access_vpn_rt': west_access_vpn_rt,
        'west_access_vpn_bd': west_access_vpn_bd,
        'west_vn_rt': west_vn_rt,

        'splicing_vlan_id': splicing_vlan_id
    }
    return configuration


class NetworkSlicingManager(object):

    def __init__(self, obj_east_site, obj_west_site, slicing_name,
                 slicing_type=constants.L2VPN_SLICING):  # noqa
        if slicing_type not in constants.SLICING_TYPE_LIST:
            raise

        self.slicing_type = slicing_type
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

    def execute_create_evpn_vpls_over_srv6_be_slicing_flow(
            self, subnet_cidr,
            east_dcn_vn_subnet_allocation_pool,
            west_dcn_vn_subnet_allocation_pool):

        flow_name = "create_l2vpn_slicing_flow"
        flow_list = [tasks.EastDCN_EVPNVxLAN(),
                     tasks.WestDCN_EVPNVxLAN(),
                     tasks.EastVPN_EVPNVPLSoSRv6BE(),
                     tasks.WestVPN_EVPNVPLSoSRv6BE()]

        flow_store = _prepare_l2vpn_slicing_configuration()
        flow_store['ns_mgr'] = self
        flow_store['subnet_cidr'] = subnet_cidr
        flow_store['east_dcn_vn_subnet_ip_pool'] = east_dcn_vn_subnet_allocation_pool  # noqa
        flow_store['west_dcn_vn_subnet_ip_pool'] = west_dcn_vn_subnet_allocation_pool  # noqa
        flow_engine = flows.get_flow(flow_name, flow_list, flow_store)
        flow_engine.run()

        flow_store['east_dcn_vn_vni'] = flow_store['east_access_vpn_vni'] = flow_engine.storage.fetch('east_vn_vni')  # noqa
        flow_store['west_dcn_vn_vni'] = flow_store['west_access_vpn_vni'] = flow_engine.storage.fetch('west_vn_vni')  # noqa
        flow_store['east_dcn_vn_uuid'] = flow_engine.storage.fetch('east_vn_uuid')  # noqa
        flow_store['west_dcn_vn_uuid'] = flow_engine.storage.fetch('west_vn_uuid')  # noqa
        return flow_store

    def execute_delete_evpn_vpls_over_srv6_be_slicing_flow(
            self,
            east_wan_vpn_bridge_domain,
            east_access_vpn_bridge_domain,
            east_access_vpn_vni,
            west_wan_vpn_bridge_domain,
            west_access_vpn_bridge_domain,
            west_access_vpn_vni):

        self.delete_evpn_vxlan_dcn(self.east_sdnc_mgr)
        self.delete_evpn_vxlan_dcn(self.west_sdnc_mgr)

        self.delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self.east_dev_mgr,
            self.obj_east_wan_node,
            wan_vpn_bd=east_wan_vpn_bridge_domain,
            access_vpn_bd=east_access_vpn_bridge_domain,
            access_vpn_vxlan_vni=east_access_vpn_vni)

        self.delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            self.west_dev_mgr,
            self.obj_west_wan_node,
            wan_vpn_bd=west_wan_vpn_bridge_domain,
            access_vpn_bd=west_access_vpn_bridge_domain,
            access_vpn_vxlan_vni=west_access_vpn_vni)

    def create_evpn_vxlan_dcn(self, sdnc_mgr, subnet_cidr,
                              subnet_allocation_pool, route_target):
        if self.slicing_type == constants.L2VPN_SLICING:
            forwarding_mode = 'l2'
        elif self.slicing_type == constants.L3VPN_SLICING:
            forwarding_mode = 'l2_l3'

        route_target = 'target:%s' % route_target
        vn_uuid = sdnc_mgr.create_virtal_network_with_user_defined_subnet(
            self.vn_name,
            subnet_cidr,
            subnet_allocation_pool,
            route_target,
            forwarding_mode)
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
