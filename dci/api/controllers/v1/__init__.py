"""Version 1 of the DCI Controller API"""

from pecan import rest
from wsme import types as wtypes

from dci.api.controllers import base
from dci.api.controllers.v1 import l2evpn_dcis
from dci.api.controllers.v1 import l3evpn_dcis
from dci.api.controllers.v1 import l3vpn_srv6_slicings
from dci.api.controllers.v1 import sites
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
    l3evpn_dcis = l3evpn_dcis.L3EVPNDCIController()
    l2evpn_dcis = l2evpn_dcis.L2EVPNDCIController()
    wan_nodes = wan_nodes.WANNodeController()
    l3vpn_srv6_slicings = l3vpn_srv6_slicings.L3VPNSRv6SlicingController()

    @expose.expose(V1)
    def get(self):
        return V1.convert()


__all__ = ('Controller',)
