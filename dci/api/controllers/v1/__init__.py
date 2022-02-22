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

"""Version 1 of the DCI Controller API"""

from pecan import rest
from wsme import types as wtypes

from dci.api.controllers import base
from dci.api.controllers.v1 import evpn_vpls_over_srv6_be_slicings
from dci.api.controllers.v1 import sites
from dci.api.controllers.v1 import test_netconf
from dci.api.controllers.v1 import wan_nodes
from dci.api import expose


class V1(base.APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version"""

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = 'v1'
        return v1


class Controller(rest.RestController):
    """Version 1 API controller root"""

    sites = sites.SiteController()
    wan_nodes = wan_nodes.WANNodeController()
    evpn_vpls_over_srv6_be_slicings = evpn_vpls_over_srv6_be_slicings.EVPNVPLSoSRv6SlicingController()  # noqa
    test_netconf = test_netconf.TestController()

    @expose.expose(V1)
    def get(self):
        return V1.convert()


__all__ = ('Controller',)
