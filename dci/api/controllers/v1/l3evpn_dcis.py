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
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.juniper import mx_api
from dci.juniper import tf_vnc_api
from dci import objects


LOG = log.getLogger(__name__)

VN_NAME_PREFIX = 'dcictl-L3EVPNDCI-'


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

    east_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

    west_site_uuid = types.uuid
    """The UUID of West Site Record."""

    west_site_subnet_cidr = wtypes.text
    """Subnet CIDR."""

    west_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

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
    """API representation of a collection of L3 EVPN DCI.
    """

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
        LOG.info(_LI("[l3evpn_dcis: get_one] UUID = %s"), uuid)
        context = pecan.request.context
        obj_l3evpn_dci = objects.L3EVPNDCI.get(context, uuid)
        return L3EVPNDCI.convert_with_links(obj_l3evpn_dci)

    @expose.expose(L3EVPNDCICollection, wtypes.text, wtypes.text, wtypes.text)
    def get_all(self, state=None, east_site_uuid=None, west_site_uuid=None):
        """Retrieve a list of L3 EVPN DCI.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        if east_site_uuid:
            filters_dict['east_site_uuid'] = east_site_uuid
        if west_site_uuid:
            filters_dict['west_site_uuid'] = west_site_uuid
        LOG.info(_LI('[l3evpn_dcis: get_all] filters = %s'), filters_dict)

        context = pecan.request.context
        obj_l3evpn_dcis = objects.L3EVPNDCI.list(context, filters=filters_dict)
        return L3EVPNDCICollection.convert_with_links(obj_l3evpn_dcis)

    def _create_l3evpn_dci_in_site(self, site, vn_name, subnet_cidr):

        # Create Tungstun Fabric Virtual Network.
        try:
            tf_client = tf_vnc_api.Client(host=site.tf_api_server_host,
                                          port=site.tf_api_server_port,
                                          username=site.tf_username,
                                          password=site.tf_password,
                                          project=site.os_project_name)
            vn_uuid = tf_client.create_virtal_network_with_user_defined_subnet(
                vn_name, subnet_cidr)
        except Exception as err:
            LOG.error(_LE("Failed to create virtual network [%(name)s], "
                          "details %(err)s"),
                      {'name': vn_name, 'err': err})
            raise err

        # Edit L3 EVPN DCI RI static route.
        try:
            mx_client = mx_api.Client(host=site.netconf_host,
                                      port=site.netconf_port,
                                      username=site.netconf_username,
                                      password=site.netconf_password)
            mx_client.create_static_route(subnet_cidr)
        except Exception as err:
            LOG.error(_LE("Failed to edit L3 EVPN DCI RI static route "
                          "[%(cidr)s], details %(err)s"),
                      {'cidr': subnet_cidr, 'err': err})

            LOG.info(_LE("Rollback virtual network [%s]..."), vn_name)
            tf_client.retry_to_delete_virtual_network(vn_name)

            raise err
        return vn_uuid

    def _soft_delete_l3evpn_dci_in_site(self, site, vn_name, subnet_cidr):

        tf_client = tf_vnc_api.Client(host=site.tf_api_server_host,
                                      port=site.tf_api_server_port,
                                      username=site.tf_username,
                                      password=site.tf_password,
                                      project=site.os_project_name)
        tf_client.retry_to_delete_virtual_network(vn_name)

        mx_client = mx_api.Client(host=site.netconf_host,
                                  port=site.netconf_port,
                                  username=site.netconf_username,
                                  password=site.netconf_password)
        mx_client.retry_to_delete_static_route(subnet_cidr)

    @expose.expose(L3EVPNDCI, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L3 EVPN DCI.
        """
        LOG.info(_LI("[l3evpn_dcis: port] Request body = %s"), req_body)
        context = pecan.request.context

        name = req_body['name']
        vn_name = VN_NAME_PREFIX + name
        try:
            east_site = objects.Site.get(context, req_body['east_site_uuid'])
            west_site = objects.Site.get(context, req_body['west_site_uuid'])
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3 EVPN DCI [%(name)s], resource "
                          "not found, defails %(err)s"),
                      {'name': name, 'err': err})
            raise err

        east_site_subnet_cidr = req_body['east_site_subnet_cidr']
        west_site_subnet_cidr = req_body['west_site_subnet_cidr']

        # East Site
        try:
            east_site_vn_uuid = self._create_l3evpn_dci_in_site(
                east_site, vn_name, east_site_subnet_cidr)
        except Exception as err:
            LOG.error(_LE("Failed to create L3 EVPN DCI for east site, "
                          "details %s"), err)
            raise err

        # West Site
        try:
            west_site_vn_uuid = self._create_l3evpn_dci_in_site(
                west_site, vn_name, west_site_subnet_cidr)
        except Exception as err:
            LOG.error(_LE("Failed to create L3 EVPN DCI for west site, "
                          "details %s"), err)

            LOG.info(_LI("Rollback east site..."))
            self._soft_delete_l3evpn_dci_in_site(east_site, vn_name,
                                                 east_site_subnet_cidr)
            raise err

        req_body['east_site_vn_uuid'] = east_site_vn_uuid
        req_body['west_site_vn_uuid'] = west_site_vn_uuid
        req_body['state'] = constants.ACTIVE
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
        LOG.info(_LI('[l3evpn_dci: delete] UUID = %s'), uuid)
        obj_l3evpn_dci = objects.L3EVPNDCI.get(context, uuid)

        name = obj_l3evpn_dci.name
        vn_name = VN_NAME_PREFIX + name

        east_site_uuid = obj_l3evpn_dci.east_site_uuid
        west_site_uuid = obj_l3evpn_dci.west_site_uuid
        try:
            east_site = objects.Site.get(context, east_site_uuid)
            west_site = objects.Site.get(context, west_site_uuid)
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3 EVPN DCI [%(name)s], resource "
                          "not found, defails %(err)s"),
                      {'name': name, 'err': err})

        try:
            self._soft_delete_l3evpn_dci_in_site(
                east_site, vn_name, obj_l3evpn_dci.east_site_subnet_cidr)
            self._soft_delete_l3evpn_dci_in_site(
                west_site, vn_name, obj_l3evpn_dci.west_site_subnet_cidr)
        except Exception as err:
            LOG.error(_LE("Failed delete L3 EVPN DCI[%(name)s], "
                          "details %(err)s"), {'name': name, 'err': err})

            LOG.info(_LI("Update L3 EVPN DCI state to `inactive`."))
            obj_l3evpn_dci.state = 'inactve'
            obj_l3evpn_dci.save(context)
            return None

        obj_l3evpn_dci.destroy(context)
