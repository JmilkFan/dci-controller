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


class EastDCN_EVPNVxLAN(task.Task):

    default_provides = set(['east_vn_vni'])

    def execute(self, ns_mgr, subnet_cidr, east_site_subnet_ip_pool, east_vn_rt,  # noqa
                *args, **kwargs):
        east_vn_vni = ns_mgr.create_evpn_vxlan_dcn(
            sdnc_mgr=ns_mgr.east_sdnc_mgr,
            subnet_cidr=subnet_cidr,
            subnet_allocation_pool=east_site_subnet_ip_pool,
            route_target=east_vn_rt)

        return {'east_vn_vni': east_vn_vni}

    def revert(self, ns_mgr, result, *args, **kwargs):
        ns_mgr.delete_evpn_vxlan_dcn(ns_mgr.east_sdnc_mgr)


class WestDCN_EVPNVxLAN(task.Task):

    default_provides = set(['west_vn_vni'])

    def execute(self, ns_mgr, subnet_cidr, west_site_subnet_ip_pool, west_vn_rt,  # noqa
                *args, **kwargs):
        west_vn_vni = ns_mgr.create_evpn_vxlan_dcn(
            sdnc_mgr=ns_mgr.west_sdnc_mgr,
            subnet_cidr=subnet_cidr,
            subnet_allocation_pool=west_site_subnet_ip_pool,
            route_target=west_vn_rt)

        return {'west_vn_vni': west_vn_vni}

    def revert(self, ns_mgr, result, *args, **kwargs):
        ns_mgr.delete_evpn_vxlan_dcn(ns_mgr.west_sdnc_mgr)


class EastVPN_EVPNVPLSoSRv6BE(task.Task):

    default_provides = set([])

    def execute(self, ns_mgr, east_wan_vpn_rd, east_wan_vpn_rt,
                east_wan_vpn_bd, east_access_vpn_rd, east_access_vpn_rt,
                east_access_vpn_bd, east_vn_vni, splicing_vlan_id,
                *args, **kwargs):
        ns_mgr.create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            dev_mgr=ns_mgr.east_dev_mgr,
            wan_vpn_rd=east_wan_vpn_rd,
            wan_vpn_rt=east_wan_vpn_rt,
            wan_vpn_bd=east_wan_vpn_bd,
            access_vpn_rd=east_access_vpn_rd,
            access_vpn_rt=east_access_vpn_rt,
            access_vpn_bd=east_access_vpn_bd,
            access_vpn_vxlan_vni=east_vn_vni,
            splicing_vlan_id=splicing_vlan_id
        )

    def revert(self, ns_mgr, east_vn_vni, east_wan_vpn_bd, east_access_vpn_bd,
               result, *args, **kwargs):
        ns_mgr.delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            dev_mgr=ns_mgr.east_dev_mgr,
            access_vpn_vxlan_vni=east_vn_vni,
            wan_vpn_bd=east_wan_vpn_bd,
            access_vpn_bd=east_access_vpn_bd
        )


class WestVPN_EVPNVPLSoSRv6BE(task.Task):

    default_provides = set([])

    def execute(self, ns_mgr, west_wan_vpn_rd, west_wan_vpn_rt,
                west_wan_vpn_bd, west_access_vpn_rd, west_access_vpn_rt,
                west_access_vpn_bd, west_vn_vni, splicing_vlan_id,
                *args, **kwargs):
        ns_mgr.create_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            dev_mgr=ns_mgr.west_dev_mgr,
            wan_vpn_rd=west_wan_vpn_rd,
            wan_vpn_rt=west_wan_vpn_rt,
            wan_vpn_bd=west_wan_vpn_bd,
            access_vpn_rd=west_access_vpn_rd,
            access_vpn_rt=west_access_vpn_rt,
            access_vpn_bd=west_access_vpn_bd,
            access_vpn_vxlan_vni=west_vn_vni,
            splicing_vlan_id=splicing_vlan_id
        )

    def revert(self, ns_mgr, west_vn_vni, west_wan_vpn_bd, west_access_vpn_bd,
               result, *args, **kwargs):
        ns_mgr.delete_evpn_vpls_over_srv6_be_wan_and_evpn_vxlan_access_vpn(
            dev_mgr=ns_mgr.west_dev_mgr,
            access_vpn_vxlan_vni=west_vn_vni,
            wan_vpn_bd=west_wan_vpn_bd,
            access_vpn_bd=west_access_vpn_bd
        )
