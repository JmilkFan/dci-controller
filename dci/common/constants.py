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

# enum of state
ACTIVE = 'ACTIVE'
INACTIVE = 'INACTIVE'

# enum of device vendor
HUAWEI = 'huawei'
JUNIPER = 'juniper'
LIST_OF_VAILD_DEVICE_VENDOR = (HUAWEI, JUNIPER)

# netmiko device mapping.
DEVICE_VENDOR_MAPPING = {
    HUAWEI: 'huaweiyang',
    JUNIPER: 'junos'
}

# enum of SRv6 routing type
BEST_EFFORT = 'be'
TRAFFIC_ENGINEERING = 'te'

# name prefix
VN_NAME_PREFIX = 'ns-dcn-l2vpn-'
WAN_VPN_NAME_PREFIX = 'ns-wan-l2vpn-'
ACCESS_VPN_NAME_PREFIX = 'ns-an-l2vpn-'

# WAN Node Roles
WAN_NODE_ROLE_DCGW = 'dcgw'
WAN_NODE_ROLE_PE = 'pe'
