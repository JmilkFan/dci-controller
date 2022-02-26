# Copyright © 2012 New Dream Network, LLC (DreamHost)
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

from http import HTTPStatus
import pecan
import wsme
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common import constants
from dci.common import exception
from dci.common.i18n import _LI
from dci import objects
from dci.task_flows import flows


LOG = log.getLogger(__name__)

NAME_PREFIX = 'dcictl-EVPNVPLSoSRv6BESlicing-'


class EVPNVPLSoSRv6BESlicing(base.APIBase):
    """API representation of a EVPN VPLS over SRv6 BE network slicing.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the EVPN VPLS over SRv6 BE network slicing."""

    name = wtypes.text
    """The name of EVPN VPLS over SRv6 BE network slicing."""

    subnet_cidr = wtypes.text
    """EVPN VPLS oser SRv6 BE Slicing Subnet CIDR."""

    state = wtypes.text
    """State of EVPN VPLS over SRv6 BE network slicing."""

    east_site_uuid = wtypes.text
    """UUID of east site."""

    east_site_subnet_allocation_pool = wtypes.text
    """Subnet allocation pool of east site."""

    west_site_uuid = wtypes.text
    """UUID of west site."""

    west_site_subnet_allocation_pool = wtypes.text
    """Subnet allocation pool of west site."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(EVPNVPLSoSRv6BESlicing, self).__init__(**kwargs)
        self.fields = []
        for field in objects.EVPNVPLSoSRv6BESlicing.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_evpn_vpls_over_srv6_be_slicing):
        api_evpn_vpls_over_srv6_be_slicing = \
            cls(**obj_evpn_vpls_over_srv6_be_slicing.as_dict())
        api_evpn_vpls_over_srv6_be_slicing.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'evpn_vpls_over_srv6_be_slicings',
                                api_evpn_vpls_over_srv6_be_slicing.uuid)
            ]
        return api_evpn_vpls_over_srv6_be_slicing


class EVPNVPLSoSRv6BESlicingCollection(base.APIBase):
    """API representation of a collection of EVPN VPLS over SRv6 BE network
    slicing.
    """

    evpn_vpls_over_srv6_be_slicings = [EVPNVPLSoSRv6BESlicing]
    """A list containing EVPN VPLS over SRv6 BE network slicing objects"""

    @classmethod
    def convert_with_links(cls, evpn_vpls_over_srv6_be_slicings):
        collection = cls()
        collection.evpn_vpls_over_srv6_be_slicings = [
            EVPNVPLSoSRv6BESlicing.convert_with_links(evpn_vpls_over_srv6_be_slicing)  # noqa
            for evpn_vpls_over_srv6_be_slicing in evpn_vpls_over_srv6_be_slicings]  # noqa
        return collection


class EVPNVPLSoSRv6BESlicingController(base.DCIController):
    """REST controller for EVPN VPLS over SRv6 BE network slicing Controller.
    """

    @expose.expose(EVPNVPLSoSRv6BESlicing, wtypes.text,
                   status_code=HTTPStatus.OK)
    def get_one(self, uuid):
        """Get a single EVPN VPLS over SRv6 BE network slicing by UUID.

        :param uuid: uuid of a EVPN VPLS over SRv6 BE network slicing.
        """
        LOG.info(_LI("[evpn_vpls_over_srv6_be_slicings: get_one] UUID = %s"), uuid)  # noqa
        context = pecan.request.context
        obj_evpn_vpls_over_srv6_be_slicing = objects.EVPNVPLSoSRv6BESlicing.get(context, uuid)  # noqa
        return EVPNVPLSoSRv6BESlicing.convert_with_links(obj_evpn_vpls_over_srv6_be_slicing)  # noqa

    @expose.expose(EVPNVPLSoSRv6BESlicingCollection, wtypes.text,
                   wtypes.text, wtypes.text, status_code=HTTPStatus.OK)
    def get_all(self, state=None, east_site_uuid=None, west_site_uuid=None):
        """Retrieve a list of EVPN VPLS over SRv6 BE network slicing.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        if east_site_uuid:
            filters_dict['east_site_uuid'] = east_site_uuid
        if west_site_uuid:
            filters_dict['west_site_uuid'] = west_site_uuid
        LOG.info(_LI("[evpn_vpls_over_srv6_be_slicings: get_all] "
                     "filters = %s"), filters_dict)

        context = pecan.request.context
        obj_evpn_vpls_over_srv6_be_slicings = \
            objects.EVPNVPLSoSRv6BESlicing.list(context, filters=filters_dict)
        return EVPNVPLSoSRv6BESlicingCollection.convert_with_links(obj_evpn_vpls_over_srv6_be_slicings)  # noqa

    @expose.expose(EVPNVPLSoSRv6BESlicing, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a EVPN VPLS over SRv6 BE network slicing.
        """
        raise exception.CapabilityNotSupported(
            "EVPN VPLS over SRv6 BE network slicing Update operation "
            "is not supported.")

    @expose.expose(EVPNVPLSoSRv6BESlicing, body=EVPNVPLSoSRv6BESlicing,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one EVPN VPLS over SRv6 BE network slicing.
        """
        req_body = req_body.as_dict()
        LOG.info(_LI("[evpn_vpls_over_srv6_be_slicings: port] Request "
                     "body = %s"), req_body)
        context = pecan.request.context

        import pdb; pdb.set_trace()  # XXX BREAKPOINT
        try:
            obj_east_site = objects.Site.get(
                context, uuid=req_body.get('east_site_uuid'))
            obj_west_site = objects.Site.get(
                context, uuid=req_body.get('west_site_uuid'))
        except exception.ResourceNotFound as err:
            raise err
        except Exception as err:
            raise err

        # NOTE(fanguiju): Just only one wan node now.
        if not obj_east_site.wan_nodes[0] or not obj_west_site.wan_nodes[0]:
            raise

        flows.execute_l2vpn_slicing_flow(obj_east_site, obj_west_site,
                                         req_body.get('subnet_cidr'),
                                         req_body.get('name'),
                                         req_body.get('east_site_subnet_allocation_pool'),  # noqa,
                                         req_body.get('west_site_subnet_allocation_pool'))  # noqa,

        req_body['state'] = constants.ACTIVE
        obj_evpn_vpls_over_srv6_be_slicing = objects.EVPNVPLSoSRv6BESlicing(context, **req_body)  # noqa
        obj_evpn_vpls_over_srv6_be_slicing.create(context)
        return EVPNVPLSoSRv6BESlicing.convert_with_links(obj_evpn_vpls_over_srv6_be_slicing)  # noqa

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one EVPN VPLS over SRv6 BE network slicing by UUID.

        :param uuid: uuid of a EVPN VPLS over SRv6 BE network slicing.
        """
        context = pecan.request.context
        LOG.info(_LI('[evpn_vpls_over_srv6_be_slicing: delete] UUID = %s'), uuid)  # noqa
        obj_evpn_vpls_over_srv6_be_slicing = objects.EVPNVPLSoSRv6BESlicing.get(context, uuid)  # noqa
        obj_evpn_vpls_over_srv6_be_slicing.destroy(context)
