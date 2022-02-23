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

from dci.flows import create_evpn_vpls_over_srv6_be_slicing_flow


class NetworkSlicingManager(object):

    def __init__(self, east_site, east_wan_node, west_site, west_wan_node,
                 *args, **kwargs):
        """Load the driver from the one specified in args, or from flags.
        """
        self.east_site = east_site
        self.east_wan_node = east_wan_node
        self.west_site = west_site
        self.west_wan_node = west_wan_node

    def create_evpn_vpls_over_srv6_be_slicing(self, subnet_cidr,
                                              east_site_subnet_ip_pool,
                                              west_site_subnet_ip_pool):
        slicing_configuration = {
            'subnet_cidr': subnet_cidr,
            'east_site': self.east_site,
            'east_wan_node': self.east_wan_node,
            'east_site_subnet_ip_pool': east_site_subnet_ip_pool,
            'west_site': self.west_site,
            'west_wan_node': self.west_wan_node,
            'west_site_subnet_ip_pool': west_site_subnet_ip_pool
        }

        flow_engine = create_evpn_vpls_over_srv6_be_slicing_flow.get_flow(
            store=slicing_configuration)
        flow_engine.run()

    def delete_evpn_vpls_over_srv6_be_slicing(self):
        pass
