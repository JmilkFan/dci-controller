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


import taskflow.engines
from taskflow.patterns import linear_flow as lt

from dci.common import utils
from dci.flows import tasks
from dci import manager


def get_flow(flow_name, flow_list, flow_store, flow_type='serial',
             *args, **kwargs):
    flow_api = lt.Flow(flow_name)
    flow_api.add(flow_list)
    return taskflow.engines.load(flow_api,
                                 engine_conf={'engine': flow_type},
                                 store=flow_store)


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


def execute_l2vpn_slicing_flow(subnet_cidr, slicing_name,
                               east_site, east_wan_node,
                               west_site, west_wan_node,
                               east_site_subnet_ip_pool,
                               west_site_subnet_ip_pool):

    flow_name = "create_l2vpn_slicing_flow"
    flow_list = [tasks.EastDCN_EVPNVxLAN(),
                 tasks.WestDCN_EVPNVxLAN(),
                 tasks.EastVPN_EVPNVPLSoSRv6BE(),
                 tasks.WestVPN_EVPNVPLSoSRv6BE()]

    flow_store = _prepare_l2vpn_slicing_configuration()
    flow_store['ns_mgr'] = manager.NetworkSlicingManager(
        east_site, east_wan_node, west_site, west_wan_node, slicing_name)
    flow_store['subnet_cidr'] = subnet_cidr
    flow_store['east_site_subnet_ip_pool'] = east_site_subnet_ip_pool
    flow_store['west_site_subnet_ip_pool'] = west_site_subnet_ip_pool

    flow_engine = get_flow(flow_name, flow_list, flow_store)
    flow_engine.run()

    flow_store['east_access_vpn_vxlan_vni'] = flow_engine.storage.fetch('east_vn_vni')  # noqa
    flow_store['west_access_vpn_vxlan_vni'] = flow_engine.storage.fetch('west_vn_vni')  # noqa
    return flow_store