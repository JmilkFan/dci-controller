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

from taskflow import task

from dci.sdnc_manager.api import SDNCManager
from dci.device_manager.api import DeviceManager


def create_evpn_vxlan_vn(sdnc_conn_ref, vn_name, subnet_cidr,
                         subnet_ip_pool, route_target):
    sdnc_mgr = SDNCManager(sdnc_conn_ref)
    vn_uuid = sdnc_mgr.sdnc_handle.\
        create_virtal_network_with_user_defined_subnet(
            vn_name, subnet_cidr, subnet_ip_pool, route_target)
    vn_vni = sdnc_mgr.sdnc_handle.get_virtual_network_vni(vn_uuid)
    return vn_vni


def delete_evpn_vxlan_vn(sdnc_conn_ref, vn_name):
    sdnc_mgr = SDNCManager(sdnc_conn_ref=sdnc_conn_ref)
    sdnc_mgr.sdnc_handle.delete_virtual_network(vn_name)


def create_evpn_vpls_over_srv6_be_vpn(device_conn_ref, vpn_configuration, vn_vni):  # noqa
    dev_mgr = DeviceManager(device_conn_ref)
    vpn_configuration['access_vpn_vxlan_vni'] = vn_vni
    return dev_mgr.create_evpn_vpls_over_srv6_be_vpn(vpn_configuration)


def delete_evpn_vpls_over_srv6_be_vpn(device_conn_ref, vpn_configuration, vn_vni):  # noqa
    dev_mgr = DeviceManager(device_conn_ref)
    vpn_configuration['access_vpn_vxlan_vni'] = vn_vni
    return dev_mgr.delete_evpn_vpls_over_srv6_be_vpn(vpn_configuration)


class EastDCN_EVPNVxLAN(task.Task):

    default_provides = set(['east_vn_vni'])

    def execute(self, east_site, vn_name, subnet_cidr,
                east_site_subnet_ip_pool, route_target,
                *args, **kwargs):
        east_vn_vni = create_evpn_vxlan_vn(east_site, vn_name, subnet_cidr,
                                           east_site_subnet_ip_pool,
                                           route_target)
        return {'east_vn_vni': east_vn_vni}

    def revert(self, east_site, vn_name, result, *args, **kwargs):
        delete_evpn_vxlan_vn(east_site, vn_name)


class WestDCN_EVPNVxLAN(task.Task):

    default_provides = set(['west_vn_vni'])

    def execute(self, west_site, vn_name, subnet_cidr,
                west_site_subnet_ip_pool, route_target,
                *args, **kwargs):
        west_vn_vni = create_evpn_vxlan_vn(west_site, vn_name, subnet_cidr,
                                           west_site_subnet_ip_pool,
                                           route_target)
        return {'west_vn_vni': west_vn_vni}

    def revert(self, west_site, vn_name, result, *args, **kwargs):
        delete_evpn_vxlan_vn(west_site, vn_name)


class EastVPN_EVPNVPLSoSRv6BE(task.Task):

    default_provides = set([])

    def execute(self, east_wan_node, east_vpn_configuration, east_vn_vni,
                *args, **kwargs):
        create_evpn_vpls_over_srv6_be_vpn(east_wan_node,
                                          east_vpn_configuration,
                                          east_vn_vni)

    def revert(self, east_wan_node, east_vpn_configuration, east_vn_vni,
               result, *args, **kwargs):
        delete_evpn_vpls_over_srv6_be_vpn(east_wan_node,
                                          east_vpn_configuration,
                                          east_vn_vni)


class WestVPN_EVPNVPLSoSRv6BE(task.Task):

    default_provides = set([])

    def execute(self, west_wan_node, west_vpn_configuration, west_vn_vni,
                *args, **kwargs):
        create_evpn_vpls_over_srv6_be_vpn(west_wan_node,
                                          west_vpn_configuration,
                                          west_vn_vni)

    def revert(self, west_wan_node, west_vpn_configuration, west_vn_vni,
               result, *args, **kwargs):
        delete_evpn_vpls_over_srv6_be_vpn(west_wan_node,
                                          west_vpn_configuration,
                                          west_vn_vni)
