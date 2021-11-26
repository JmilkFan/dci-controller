from http import HTTPStatus
import pecan
import wsme
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci import objects
from dci.common import exception
from dci.common.i18n import _LE
from dci.juniper import mx_api
from dci.juniper import tf_vnc_api


LOG = log.getLogger(__name__)


class L3EVPNDCI(base.APIBase):
    """API representation of a L3 EVPN DCI.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the L3 EVPN DCI."""

    name = wtypes.text
    """The name of L3 EVPN DCI."""

    east_site_uuid = types.uuid
    """The UUID of East Site Record."""

    east_site_subnet_cidr = wtypes.text
    """Subnet CIDR."""

    west_site_uuid = types.uuid
    """The UUID of West Site Record."""

    west_site_subnet_cidr = wtypes.text
    """Subnet CIDR."""

    state = wtypes.text
    """State of L3 EVPN DCI."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(L3EVPNDCI, self).__init__(**kwargs)
        self.fields = []
        for field in objects.L3EVPNDCI.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_l3evpn_dci):
        api_l3evpn_dci = cls(**obj_l3evpn_dci.as_dict())
        api_l3evpn_dci.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'l3evpn_dcis', api_l3evpn_dci.uuid)
            ]
        return api_l3evpn_dci


class L3EVPNDCICollection(base.APIBase):
    """API representation of a collection of L3 EVPN DCI."""

    l3evpn_dcis = [L3EVPNDCI]
    """A list containing L3 EVPN DCI objects"""

    @classmethod
    def convert_with_links(cls, l3evpn_dcis):
        collection = cls()
        collection.l3evpn_dcis = [L3EVPNDCI.convert_with_links(l3evpn_dci)
                                  for l3evpn_dci in l3evpn_dcis]
        return collection


class L3EVPNDCIController(base.DCIController):
    """REST controller for L3 EVPN DCI Controller.
    """

    @expose.expose(L3EVPNDCI, wtypes.text)
    def get_one(self, uuid):
        """Get a single L3 EVPN DCI by UUID.

        :param uuid: uuid of a L3 EVPN DCI.
        """
        LOG.info("[l3evpn_dcis:get_one] UUID = (%s)", uuid)
        context = pecan.request.context
        obj_l3evpn_dci = objects.L3EVPNDCI.get(context, uuid)
        return L3EVPNDCI.convert_with_links(obj_l3evpn_dci)

    @expose.expose(L3EVPNDCICollection, wtypes.text)
    def get_all(self, state=None):
        """Retrieve a list of L3 EVPN DCI.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        context = pecan.request.context
        obj_l3evpn_dcis = objects.L3EVPNDCI.list(context, filters=filters_dict)
        LOG.info('[l3evpn_dcis:get_all] Returned: %s', obj_l3evpn_dcis)
        return L3EVPNDCICollection.convert_with_links(obj_l3evpn_dcis)

    def _create_l3evpn_dci_in_site(self, name, site_uuid, subnet_cidr):
        # Step2. Create a Virtual Network
        vn_name = 'dci-controller-setup-' + name
        tf_client = tf_vnc_api.Client(site_uuid)
        tf_client.create_virtal_network_with_user_defined_subnet(vn_name,
                                                                 subnet_cidr)

        # Step3. Set a EVPN Type 5 DCI static route to vMX.
        mx_client = mx_api.Client()
        mx_client.edit_l3evpn_dci_routing_instance_static_route(
            action='set', site_uuid=site_uuid, subnet_cidr=subnet_cidr)

    def _clean_l3evpn_dci_in_site(self, name, site_uuid, subnet_cidr):
         # Step2. Delete a Virtual Network
        vn_name = 'dci-controller-setup-' + name
        tf_client = tf_vnc_api.Client(site_uuid)
        tf_client.delete_virtual_network(vn_name)

        # Step3. Delete a EVPN Type 5 DCI static route to vMX.
        mx_client = mx_api.Client()
        mx_client.edit_l3evpn_dci_routing_instance_static_route(
            action='delete', site_uuid=site_uuid, subnet_cidr=subnet_cidr)

    @expose.expose(L3EVPNDCI, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L3 EVPN DCI.
        """
        LOG.info("[l3evpn_dcis:port] Req = (%s)", req_body)
        context = pecan.request.context

        name = req_body['name']
        east_site_uuid = req_body['east_site_uuid']
        east_site_subnet_cidr = req_body['east_site_subnet_cidr']
        west_site_uuid = req_body['west_site_uuid']
        west_site_subnet_cidr = req_body['west_site_subnet_cidr']

        try:
            # Step1. Loop two DCI sites.
            # TODO(fanguiju): Use two concurrent tasks.
            self._create_l3evpn_dci_in_site(name,
                                            east_site_uuid,
                                            east_site_subnet_cidr)
            # self._create_l3evpn_dci_in_site(name,
            #                                 west_site_uuid,
            #                                 west_site_subnet_cidr)
        except Exception as err:
            # TODO(fanguiju): Rollback
            LOG.error(_LE("Failed create L3 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': exc.err})
            import pdb; pdb.set_trace()  # XXX BREAKPOINT

        # Step4. Update the L3 EVPN DCI state.
        req_body['state'] = 'active'
        obj_l3evpn_dci = objects.L3EVPNDCI(context, **req_body)
        obj_l3evpn_dci.create(context)

        return L3EVPNDCI.convert_with_links(obj_l3evpn_dci)

    @expose.expose(L3EVPNDCI, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a L3 EVPN DCI.
        """
        raise exception.CapabilityNotSupported(
            "L3 EVPN DCI Update operation is not supported")

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one L3 EVPN DCI by UUID.

        :param uuid: uuid of a L3 EVPN DCI.
        """
        context = pecan.request.context
        LOG.info('[l3evpn_dci:delete] UUID = (%s)', uuid)
        obj_l3evpn_dci = objects.L3EVPNDCI.get(context, uuid)

        name = obj_l3evpn_dci.name
        east_site_uuid = obj_l3evpn_dci.east_site_uuid
        east_site_subnet_cidr = obj_l3evpn_dci.east_site_subnet_cidr
        west_site_uuid = obj_l3evpn_dci.west_site_uuid
        west_site_subnet_cidr = obj_l3evpn_dci.west_site_subnet_cidr

        try:
            # Step1. Loop two DCI sites.
            # TODO(fanguiju): Use two concurrent tasks.
            self._clean_l3evpn_dci_in_site(name,
                                           east_site_uuid,
                                           east_site_subnet_cidr)
            # self._clean_l3evpn_dci_in_site(name,
            #                                west_site_uuid,
            #                                west_site_subnet_cidr)
        except Exception as err:
            # TODO(fanguiju): Rollback
            LOG.error(_LE("Failed delete L3 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': exc.err})
            import pdb; pdb.set_trace()  # XXX BREAKPOINT

        # Step4. Delete the L3 EVPN DCI record.
        obj_l3evpn_dci.destroy(context)
