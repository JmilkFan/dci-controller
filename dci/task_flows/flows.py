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

from dci.flows import tasks


def get_flow(flow_name, flow_list, flow_store, flow_type='serial',
             *args, **kwargs):
    flow_api = lt.Flow(flow_name)
    flow_api.add(flow_list)
    return taskflow.engines.load(flow_api,
                                 engine_conf={'engine': flow_type},
                                 store=flow_store)


def get_create_evpn_vpls_over_srv6_be_slicing_flow(store, *args, **kwargs):

    flow_name = "create_evpn_vpls_over_srv6_be_slicing_flow"
    flow_list = [tasks.EastDCN_EVPNVxLAN(),
                 tasks.WestDCN_EVPNVxLAN(),
                 tasks.EastVPN_EVPNVPLSoSRv6BE(),
                 tasks.WestVPN_EVPNVPLSoSRv6BE()]
    flow_store = {}
    return get_flow(flow_name, flow_list, flow_store, *args, **kwargs)
