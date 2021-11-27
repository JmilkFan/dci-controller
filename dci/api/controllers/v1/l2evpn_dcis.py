from http import HTTPStatus
import pecan
import random
import wsme
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common import exception
from dci.common.i18n import _LE
from dci.juniper import mx_api
from dci.juniper import tf_vnc_api
from dci import objects


LOG = log.getLogger(__name__)


class L2EVPNDCI(base.APIBase):
    """API representation of a L2 EVPN DCI.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the L2 EVPN DCI."""

    name = wtypes.text
    """The name of L2 EVPN DCI."""

    east_site_uuid = types.uuid
    """The UUID of East Site Record."""

    west_site_uuid = types.uuid
    """The UUID of West Site Record."""

    subnet_cidr = wtypes.text
    """Subnet CIDR."""

    east_site_subnet_allocation_pool = wtypes.text
    """Subnet allocation IP address pool."""

    west_site_subnet_allocation_pool = wtypes.text
    """Subnet allocation IP address pool."""

    vlan_id = wtypes.IntegerType()
    """VLAN ID between fase-2-tf and fase-2-dci"""

    route_target = wtypes.text
    """Virtual Network Route Target."""

    state = wtypes.text
    """State of L2 EVPN DCI."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(L2EVPNDCI, self).__init__(**kwargs)
        self.fields = []
        for field in objects.L2EVPNDCI.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_l2evpn_dci):
        api_l2evpn_dci = cls(**obj_l2evpn_dci.as_dict())
        api_l2evpn_dci.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'l2evpn_dcis', api_l2evpn_dci.uuid)
            ]
        return api_l2evpn_dci


class L2EVPNDCICollection(base.APIBase):
    """API representation of a collection of L2 EVPN DCI."""

    l2evpn_dcis = [L2EVPNDCI]
    """A list containing L2 EVPN DCI objects"""

    @classmethod
    def convert_with_links(cls, l2evpn_dcis):
        collection = cls()
        collection.l2evpn_dcis = [L2EVPNDCI.convert_with_links(l2evpn_dci)
                                  for l2evpn_dci in l2evpn_dcis]
        return collection


class L2EVPNDCIController(base.DCIController):
    """REST controller for L2 EVPN DCI Controller.
    """

    @expose.expose(L2EVPNDCI, wtypes.text)
    def get_one(self, uuid):
        """Get a single L2 EVPN DCI by UUID.

        :param uuid: uuid of a L2 EVPN DCI.
        """
        LOG.info("[l2evpn_dcis:get_one] UUID = (%s)", uuid)
        context = pecan.request.context
        obj_l2evpn_dci = objects.L2EVPNDCI.get(context, uuid)
        return L2EVPNDCI.convert_with_links(obj_l2evpn_dci)

    @expose.expose(L2EVPNDCICollection, wtypes.text)
    def get_all(self, state=None):
        """Retrieve a list of L2 EVPN DCI.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        context = pecan.request.context
        obj_l2evpn_dcis = objects.L2EVPNDCI.list(context, filters=filters_dict)
        LOG.info('[l2evpn_dcis:get_all] Returned: %s', obj_l2evpn_dcis)
        return L2EVPNDCICollection.convert_with_links(obj_l2evpn_dcis)

    def _create_l2evpn_dci_in_site(self, name, site_uuid, subnet_cidr,
                                   subnet_allocation_pool, route_target,
                                   vlan_id):
        # Step2. Create a Virtual Network
        vn_name = 'dci-controller-setup-' + name
        tf_client = tf_vnc_api.Client(site_uuid)
        vn_uuid = tf_client.create_virtal_network_with_user_defined_subnet(
            vn_name, subnet_cidr, subnet_allocation_pool, route_target)

        vn_vni = tf_client.get_virtual_network_vni(vn_uuid)

        # Step3. Set a EVPN Type 2 DCI static route to vMX.
        mx_client = mx_api.Client()
        mx_client.edit_l2evpn_dci_routing_instance_bridge_domain(
            action='set',
            site_uuid=site_uuid,
            vn_name=vn_name,
            vn_vni=vn_vni,
            vlan_id=vlan_id,
            route_target=route_target)

    def _clean_l2evpn_dci_in_site(self, name, site_uuid, subnet_cidr,
                                  route_target, vlan_id):
        # Step2. Delete a Virtual Network
        vn_name = 'dci-controller-setup-' + name
        tf_client = tf_vnc_api.Client(site_uuid)
        vn_o = tf_client.get_virtual_network_obj_by_name(vn_name)
        vn_vni = vn_o.virtual_network_network_id
        tf_client.delete_virtual_network(vn_name)

        # Step3. Delete a EVPN Type 5 DCI static route to vMX.
        mx_client = mx_api.Client()
        mx_client.edit_l2evpn_dci_routing_instance_bridge_domain(
            action='delete',
            site_uuid=site_uuid,
            vn_name=vn_name,
            vn_vni=vn_vni,
            vlan_id=vlan_id,
            route_target=route_target)

    @expose.expose(L2EVPNDCI, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L2 EVPN DCI.
        """
        LOG.info("[l2evpn_dcis:port] Req = (%s)", req_body)
        context = pecan.request.context

        name = req_body['name']
        east_site_uuid = req_body['east_site_uuid']
        west_site_uuid = req_body['west_site_uuid']
        subnet_cidr = req_body['subnet_cidr']
        east_site_subnet_allocation_pool = req_body['east_site_subnet_allocation_pool']  # noqa
        west_site_subnet_allocation_pool = req_body['west_site_subnet_allocation_pool']  # noqa
        route_target = req_body['route_target']

        # TODO(fanguiju): Check the uniqueness of the VLAN ID.
        vlan_id = random.randint(2, 4094)

        try:
            pass
            # Step1. Loop two DCI sites.
            # TODO(fanguiju): Use two concurrent tasks.
            self._create_l2evpn_dci_in_site(
                name, east_site_uuid, subnet_cidr,
                east_site_subnet_allocation_pool,
                route_target, vlan_id)

            self._create_l2evpn_dci_in_site(
                name, west_site_uuid, subnet_cidr,
                west_site_subnet_allocation_pool,
                route_target, vlan_id)
        except Exception as err:
            # TODO(fanguiju): Rollback
            LOG.error(_LE("Failed create L2 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': err})
            raise err

        # Step4. Update the L2 EVPN DCI state.
        req_body['state'] = 'active'
        req_body['vlan_id'] = vlan_id
        obj_l2evpn_dci = objects.L2EVPNDCI(context, **req_body)
        obj_l2evpn_dci.create(context)

        return L2EVPNDCI.convert_with_links(obj_l2evpn_dci)

    @expose.expose(L2EVPNDCI, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a L2 EVPN DCI.
        """
        raise exception.CapabilityNotSupported(
            "L2 EVPN DCI Update operation is not supported")

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one L2 EVPN DCI by UUID.

        :param uuid: uuid of a L2 EVPN DCI.
        """
        context = pecan.request.context
        LOG.info('[l2evpn_dci:delete] UUID = (%s)', uuid)
        obj_l2evpn_dci = objects.L2EVPNDCI.get(context, uuid)

        name = obj_l2evpn_dci.name
        east_site_uuid = obj_l2evpn_dci.east_site_uuid
        west_site_uuid = obj_l2evpn_dci.west_site_uuid
        subnet_cidr = obj_l2evpn_dci.subnet_cidr
        route_target = obj_l2evpn_dci.route_target
        vlan_id = obj_l2evpn_dci.vlan_id

        try:
            pass
            # Step1. Loop two DCI sites.
            # TODO(fanguiju): Use two concurrent tasks.
            self._clean_l2evpn_dci_in_site(name,
                                           east_site_uuid,
                                           subnet_cidr,
                                           route_target,
                                           vlan_id)
            self._clean_l2evpn_dci_in_site(name,
                                           west_site_uuid,
                                           subnet_cidr,
                                           route_target,
                                           vlan_id)
        except Exception as err:
            # TODO(fanguiju): Rollback
            LOG.error(_LE("Failed delete L2 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': err})
            raise err

        # Step4. Delete the L2 EVPN DCI record.
        obj_l2evpn_dci.destroy(context)
