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
from dci.common import constants
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.juniper import mx_api
from dci.juniper import tf_vnc_api
from dci import objects


LOG = log.getLogger(__name__)

VN_NAME_PREFIX = 'dci-controller-L2EVPNDCI-'
VLAN_ID_RANGE = [1000, 2000]
ROUTE_TARGET_RANGE = [1000, 2000]
DCI_EVPN_TYPE2_VNI = [1000, 2000]


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

    east_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

    west_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

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
        LOG.info(_LI("[l2evpn_dcis: get_one] UUID = %s"), uuid)
        context = pecan.request.context
        obj_l2evpn_dci = objects.L2EVPNDCI.get(context, uuid)
        return L2EVPNDCI.convert_with_links(obj_l2evpn_dci)

    @expose.expose(L2EVPNDCICollection, wtypes.text, wtypes.text, wtypes.text)
    def get_all(self, state=None, east_site_uuid=None, west_site_uuid=None):
        """Retrieve a list of L2 EVPN DCI.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        if east_site_uuid:
            filters_dict['east_site_uuid'] = east_site_uuid
        if west_site_uuid:
            filters_dict['west_site_uuid'] = west_site_uuid
        LOG.info(_LI('[l2evpn_dcis: get_all] filters = %s'), filters_dict)

        context = pecan.request.context
        obj_l2evpn_dcis = objects.L2EVPNDCI.list(context, filters=filters_dict)
        return L2EVPNDCICollection.convert_with_links(obj_l2evpn_dcis)

    def _create_l2evpn_dci_in_site(self, site, vn_name, subnet_cidr,
                                   subnet_allocation_pool, vn_route_target,
                                   inter_vlan_id, dci_vni):
        # Create Tungstun Fabric Virtual Network.
        try:
            tf_client = tf_vnc_api.Client(host=site.tf_api_server_host,
                                          port=site.tf_api_server_port,
                                          username=site.tf_username,
                                          password=site.tf_password,
                                          project=site.os_project_name)
            vn_uuid = tf_client.create_virtal_network_with_user_defined_subnet(
                vn_name, subnet_cidr, subnet_allocation_pool, vn_route_target)
        except Exception as err:
            LOG.error(_LE("Failed to create virtual network [%(name)s], "
                          "details %(err)s"),
                      {'name': vn_name, 'err': err})
            raise err

        vn_vni = tf_client.get_virtual_network_vni(vn_uuid)

        # Create L2 EVPN DCI RI bridge domain.
        try:
            mx_client = mx_api.Client(host=site.netconf_host,
                                      port=site.netconf_port,
                                      username=site.netconf_username,
                                      password=site.netconf_password)
            mx_client.create_bridge_domain(
                vn_name=vn_name,
                vn_vni=vn_vni,
                vn_route_target=vn_route_target,
                inter_vlan_id=inter_vlan_id,
                dci_vni=dci_vni)
        except Exception as err:
            LOG.error(_LE("Failed to Create L2 EVPN DCI RI bridge domain "
                          "details %s"), err)

            LOG.info(_LE("Rollback virtual network [%s]..."), vn_name)
            tf_client.retry_to_delete_virtual_network(vn_name)
            raise err

        return vn_uuid

    def _soft_delete_l2evpn_dci_in_site(self, site, vn_name, subnet_cidr,
                                        subnet_allocation_pool,
                                        vn_route_target,
                                        inter_vlan_id, dci_vni):
        tf_client = tf_vnc_api.Client(host=site.tf_api_server_host,
                                      port=site.tf_api_server_port,
                                      username=site.tf_username,
                                      password=site.tf_password,
                                      project=site.os_project_name)
        vn_o = tf_client.get_virtual_network_obj_by_name(vn_name)
        vn_vni = vn_o.virtual_network_network_id
        tf_client.retry_to_delete_virtual_network(vn_name)

        mx_client = mx_api.Client(host=site.netconf_host,
                                  port=site.netconf_port,
                                  username=site.netconf_username,
                                  password=site.netconf_password)
        mx_client.retry_to_delete_bridge_domain(vn_name, vn_vni,
                                                vn_route_target,
                                                inter_vlan_id, dci_vni)

    def _get_used_vid_and_vni_in_dci_bd(self, site):
        mx_client = mx_api.Client(host=site.netconf_host,
                                  port=site.netconf_port,
                                  username=site.netconf_username,
                                  password=site.netconf_password)
        inter_vlan_id_list, dci_vni_list = \
            mx_client.get_used_vid_and_vni_in_dci_bridge_domains()
        return inter_vlan_id_list, dci_vni_list

    def _get_free_vid_and_vni_in_dci_bd(self, east_site, west_site):
        e_inter_vlan_id_list, e_dci_vni_list = \
            self._get_used_vid_and_vni_in_dci_bd(east_site)
        w_inter_vlan_id_list, w_dci_vni_list = \
            self._get_used_vid_and_vni_in_dci_bd(west_site)

        # FIXME(fanguiju): Possible permanent circulation problems !!
        while True:
            tmp_vid = random.randint(*VLAN_ID_RANGE)
            if tmp_vid not in (set(e_inter_vlan_id_list) | set(w_inter_vlan_id_list)):  # noqa
                inter_vlan_id = tmp_vid
                break
        while True:
            tmp_vni = random.randint(*DCI_EVPN_TYPE2_VNI)
            if tmp_vni not in (set(e_dci_vni_list) | set(w_dci_vni_list)):
                dci_vni = tmp_vni
                break

        LOG.info(_LI("Selete free inter_vlan_id %(vid)s and dci_vni %(vni)s"),
                 {'vid': inter_vlan_id, 'vni': dci_vni})
        return inter_vlan_id, dci_vni

    def _get_vn_route_target(self):
        num = random.randint(*ROUTE_TARGET_RANGE)
        route_target = 'target:%(asn)s:%(target)s' % {'asn': num,
                                                      'target': num}
        return route_target

    @expose.expose(L2EVPNDCI, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L2 EVPN DCI.
        """
        LOG.info(_LI("[l2evpn_dcis: port] Request body = %s"), req_body)
        context = pecan.request.context

        name = req_body['name']
        vn_name = VN_NAME_PREFIX + name

        try:
            east_site = objects.Site.get(context, req_body['east_site_uuid'])
            west_site = objects.Site.get(context, req_body['west_site_uuid'])
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L2 EVPN DCI [%(name)s], resource "
                          "not found, defails %(err)s"),
                      {'name': name, 'err': err})
            raise err

        inter_vlan_id, dci_vni = self._get_free_vid_and_vni_in_dci_bd(
            east_site, west_site)
        vn_route_target = self._get_vn_route_target()

        subnet_cidr = req_body['subnet_cidr']
        east_site_subnet_allocation_pool = req_body['east_site_subnet_allocation_pool']  # noqa
        west_site_subnet_allocation_pool = req_body['west_site_subnet_allocation_pool']  # noqa

        # East Site
        try:
            east_site_vn_uuid = self._create_l2evpn_dci_in_site(
                east_site, vn_name, subnet_cidr,
                east_site_subnet_allocation_pool,
                vn_route_target, inter_vlan_id, dci_vni)
        except Exception as err:
            LOG.error(_LE("Failed to create L2 EVPN DCI for east site, "
                          "details %s"), err)
            raise err

        # West Site
        try:
            west_site_vn_uuid = self._create_l2evpn_dci_in_site(
                west_site, vn_name, subnet_cidr,
                west_site_subnet_allocation_pool,
                vn_route_target, inter_vlan_id, dci_vni)
        except Exception as err:
            LOG.error(_LE("Failed to create L2 EVPN DCI for west site, "
                          "details %s"), err)

            LOG.info(_LI("Rollback east site..."))
            self._soft_delete_l2evpn_dci_in_site(
                east_site, vn_name, subnet_cidr,
                east_site_subnet_allocation_pool,
                vn_route_target, inter_vlan_id, dci_vni)
            raise err

        # Step4. Update the L2 EVPN DCI state.
        req_body['state'] = constants.ACTIVE
        req_body['inter_vlan_id'] = inter_vlan_id
        req_body['dci_vni'] = dci_vni
        req_body['vn_route_target'] = vn_route_target
        req_body['east_site_vn_uuid'] = east_site_vn_uuid
        req_body['west_site_vn_uuid'] = west_site_vn_uuid

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
        LOG.info(_LI('[l2evpn_dci: delete] UUID = %s'), uuid)
        context = pecan.request.context
        obj_l2evpn_dci = objects.L2EVPNDCI.get(context, uuid)

        name = obj_l2evpn_dci.name
        vn_name = VN_NAME_PREFIX + name

        east_site_uuid = obj_l2evpn_dci.east_site_uuid
        east_site_subnet_allocation_pool = obj_l2evpn_dci.east_site_subnet_allocation_pool  # noqa
        west_site_uuid = obj_l2evpn_dci.west_site_uuid
        west_site_subnet_allocation_pool = obj_l2evpn_dci.west_site_subnet_allocation_pool  # noqa

        subnet_cidr = obj_l2evpn_dci.subnet_cidr
        vn_route_target = obj_l2evpn_dci.vn_route_target
        inter_vlan_id = obj_l2evpn_dci.inter_vlan_id
        dci_vni = obj_l2evpn_dci.dci_vni

        try:
            east_site = objects.Site.get(context, east_site_uuid)
            west_site = objects.Site.get(context, west_site_uuid)
        except Exception as err:
            LOG.error(_LE("Failed to create L2 EVPN DCI [%(name)s], resource "
                          "not found, defails %(err)s"),
                      {'name': name, 'err': err})

        try:
            self._soft_delete_l2evpn_dci_in_site(
                east_site, vn_name, subnet_cidr,
                east_site_subnet_allocation_pool,
                vn_route_target, inter_vlan_id, dci_vni)

            self._soft_delete_l2evpn_dci_in_site(
                west_site, vn_name, subnet_cidr,
                west_site_subnet_allocation_pool,
                vn_route_target, inter_vlan_id, dci_vni)

        except Exception as err:
            LOG.error(_LE("Failed delete L2 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': err})

            LOG.info(_LI("Update L2 EVPN DCI state to `inactive`."))
            obj_l2evpn_dci.state = 'inactve'
            obj_l2evpn_dci.save(context)
            return None

        obj_l2evpn_dci.destroy(context)
