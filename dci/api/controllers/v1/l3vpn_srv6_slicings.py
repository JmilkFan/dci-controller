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
from dci.huawei import netengine_api
from dci.juniper import tf_vnc_api
from dci import objects


LOG = log.getLogger(__name__)

VN_NAME_PREFIX = 'dci-controller-L3VPNSRv6Slicing-'


class L3VPNSRv6Slicing(base.APIBase):
    """API representation of a L3VPN over SRv6 network slicing.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the L3VPN over SRv6 network slicing."""

    name = wtypes.text
    """The name of L3VPN over SRv6 network slicing."""

    routing_type = wtypes.text
    """SRv6 Routing Type."""

    ingress_node = wtypes.text
    """SRv6 VPN Ingress Node."""

    egress_node = wtypes.text
    """SRv6 VPN Egress Node."""

    east_site_subnet_cidr = wtypes.text
    """Subnet CIDR."""

    east_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

    west_site_subnet_cidr = wtypes.text
    """Subnet CIDR."""

    west_site_vn_uuid = wtypes.text
    """UUID of Virtual Network."""

    state = wtypes.text
    """State of L3VPN over SRv6 network slicing."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(L3VPNSRv6Slicing, self).__init__(**kwargs)
        self.fields = []
        for field in objects.L3VPNSRv6Slicing.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_l3vpn_srv6_slicing):
        api_l3vpn_srv6_slicing = cls(**obj_l3vpn_srv6_slicing.as_dict())
        api_l3vpn_srv6_slicing.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'l3vpn_srv6_slicings',
                                api_l3vpn_srv6_slicing.uuid)
            ]
        return api_l3vpn_srv6_slicing


class L3VPNSRv6SlicingCollection(base.APIBase):
    """API representation of a collection of L3VPN over SRv6 network slicing.
    """

    l3vpn_srv6_slicings = [L3VPNSRv6Slicing]
    """A list containing L3VPN over SRv6 network slicing objects"""

    @classmethod
    def convert_with_links(cls, l3vpn_srv6_slicings):
        collection = cls()
        collection.l3vpn_srv6_slicings = [
            L3VPNSRv6Slicing.convert_with_links(l3vpn_srv6_slicing)
            for l3vpn_srv6_slicing in l3vpn_srv6_slicings]
        return collection


class L3VPNSRv6SlicingController(base.DCIController):
    """REST controller for L3VPN over SRv6 network slicing Controller.
    """

    @expose.expose(L3VPNSRv6Slicing, wtypes.text)
    def get_one(self, uuid):
        """Get a single L3VPN over SRv6 network slicing by UUID.

        :param uuid: uuid of a L3VPN over SRv6 network slicing.
        """
        LOG.info(_LI("[l3vpn_srv6_slicings: get_one] UUID = %s"), uuid)
        context = pecan.request.context
        obj_l3vpn_srv6_slicing = objects.L3VPNSRv6Slicing.get(context, uuid)
        return L3VPNSRv6Slicing.convert_with_links(obj_l3vpn_srv6_slicing)

    @expose.expose(L3VPNSRv6SlicingCollection, wtypes.text,
                   wtypes.text, wtypes.text)
    def get_all(self, state=None, east_site_uuid=None, west_site_uuid=None):
        """Retrieve a list of L3VPN over SRv6 network slicing.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state
        if east_site_uuid:
            filters_dict['east_site_uuid'] = east_site_uuid
        if west_site_uuid:
            filters_dict['west_site_uuid'] = west_site_uuid
        LOG.info(_LI('[l3vpn_srv6_slicings: get_all] filters = %s'),
                 filters_dict)

        context = pecan.request.context
        obj_l3vpn_srv6_slicings = objects.L3VPNSRv6Slicing.list(
            context, filters=filters_dict)
        return L3VPNSRv6SlicingCollection.convert_with_links(obj_l3vpn_srv6_slicings)  # noqa

    def _create_l3vpn_srv6_slicing_in_site(self, site, vn_name,
                                           subnet_cidr, wan_node, node_type):

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

        # Edit L3VPN over SRv6 network slicing WAN node.
        try:
            ne_client = netengine_api.Client(
                host=wan_node.ssh_host,
                port=wan_node.ssh_port,
                username=wan_node.ssh_username,
                password=wan_node.ssh_password)
            if node_type == 'ingress':
                ne_client.setup_l3vpn_srv6_be_ingress_node(action='create')
            elif node_type == 'egress':
                ne_client.setup_l3vpn_srv6_be_egress_node(action='create')
            else:
                raise exception.InvalidL3VPNSRv6SlicingNodeType(type=node_type)
        except Exception as err:
            LOG.error(_LE("Failed to edit L3VPN over SRv6 network slicing WAN "
                          "node [%(host)s], details %(err)s"),
                      {'host': wan_node.ssh_host, 'err': err})

            LOG.info(_LE("Rollback virtual network [%s]..."), vn_name)
            tf_client.retry_to_delete_virtual_network(vn_name)
            raise err

        return vn_uuid

    def _soft_delete_l3vpn_srv6_slicing_in_site(self, site, vn_name,
                                                subnet_cidr, wan_node,
                                                node_type):

        tf_client = tf_vnc_api.Client(host=site.tf_api_server_host,
                                      port=site.tf_api_server_port,
                                      username=site.tf_username,
                                      password=site.tf_password,
                                      project=site.os_project_name)
        tf_client.retry_to_delete_virtual_network(vn_name)

        ne_client = netengine_api.Client(
            host=wan_node.ssh_host,
            port=site.ssh_port,
            username=site.ssh_username,
            password=site.ssh_password)
        if node_type == 'ingress':
            ne_client.setup_l3vpn_srv6_be_ingress_node(action='delete')
        elif node_type == 'egress':
            ne_client.setup_l3vpn_srv6_be_egress_node(action='delete')
        else:
            raise exception.InvalidL3VPNSRv6SlicingNodeType(type=node_type)

    @expose.expose(L3VPNSRv6Slicing, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L3VPN over SRv6 network slicing.
        """
        LOG.info(_LI("[l3vpn_srv6_slicings: port] Request body = %s"),
                 req_body)
        context = pecan.request.context

        name = req_body['name']
        vn_name = VN_NAME_PREFIX + name
        try:
            east_site = objects.Site.get(context, req_body['east_site_uuid'])
            west_site = objects.Site.get(context, req_body['west_site_uuid'])
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
                          "[%(name)s], Sites resource not found, "
                          "defails %(err)s"),
                      {'name': name, 'err': err})
            raise err

        try:
            ingress_node = objects.WANNode.get(context, req_body['ingress_node'])  # noqa
            egress_node = objects.WANNode.get(context, req_body['egress_node'])
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
                          "[%(name)s], WAN node resource not found, "
                          "defails %(err)s"),
                      {'name': name, 'err': err})
            raise err

        east_site_subnet_cidr = req_body['east_site_subnet_cidr']
        west_site_subnet_cidr = req_body['west_site_subnet_cidr']

        # East Site
        #try:
        #    east_site_vn_uuid = self._create_l3vpn_srv6_slicing_in_site(
        #        east_site, vn_name, east_site_subnet_cidr,
        #        ingress_node, node_type='ingress')
        #except Exception as err:
        #    LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
        #                  "for east site, details %s"), err)
        #    raise err

        # West Site
        #try:
        #    west_site_vn_uuid = self._create_l3vpn_srv6_slicing_in_site(
        #        west_site, vn_name, west_site_subnet_cidr,
        #        egress_node, node_type='egress')
        #except Exception as err:
        #    LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
        #                  "for west site, details %s"), err)

        #    LOG.info(_LI("Rollback east site..."))
        #    self._soft_delete_l3vpn_srv6_slicing_in_site(
        #        east_site, vn_name, east_site_subnet_cidr,
        #        ingress_node, node_type='ingress')
        #    raise err

        #req_body['east_site_vn_uuid'] = east_site_vn_uuid
        #req_body['west_site_vn_uuid'] = west_site_vn_uuid

        req_body['state'] = constants.ACTIVE
        obj_l3vpn_srv6_slicing = objects.L3VPNSRv6Slicing(context, **req_body)
        obj_l3vpn_srv6_slicing.create(context)
        return L3VPNSRv6Slicing.convert_with_links(obj_l3vpn_srv6_slicing)

    @expose.expose(L3VPNSRv6Slicing, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a L3VPN over SRv6 network slicing.
        """
        raise exception.CapabilityNotSupported(
            "L3VPN over SRv6 network slicing Update operation "
            "is not supported.")

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one L3VPN over SRv6 network slicing by UUID.

        :param uuid: uuid of a L3VPN over SRv6 network slicing.
        """
        context = pecan.request.context
        LOG.info(_LI('[l3vpn_srv6_slicing: delete] UUID = %s'), uuid)
        obj_l3vpn_srv6_slicing = objects.L3VPNSRv6Slicing.get(context, uuid)

        name = obj_l3vpn_srv6_slicing.name
        vn_name = VN_NAME_PREFIX + name

        east_site_uuid = obj_l3vpn_srv6_slicing.east_site_uuid
        west_site_uuid = obj_l3vpn_srv6_slicing.west_site_uuid
        try:
            east_site = objects.Site.get(context, east_site_uuid)
            west_site = objects.Site.get(context, west_site_uuid)
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
                          "[%(name)s], Site resource not found, "
                          "defails %(err)s"),
                      {'name': name, 'err': err})

        ingress_node_uuid = obj_l3vpn_srv6_slicing.ingress_node
        egress_node_uuid = obj_l3vpn_srv6_slicing.egress_node
        try:
            ingress_node = objects.WANNode.get(context, ingress_node_uuid)
            egress_node = objects.WANNode.get(context, egress_node_uuid)
        except exception.ResourceNotFound as err:
            LOG.error(_LE("Failed to create L3VPN over SRv6 network slicing "
                          "[%(name)s], WAN node resource not found, "
                          "defails %(err)s"),
                      {'name': name, 'err': err})

        #try:
        #    self._soft_delete_l3vpn_srv6_slicing_in_site(
        #        east_site, vn_name,
        #        obj_l3vpn_srv6_slicing.east_site_subnet_cidr,
        #        ingress_node, node_type='ingress')
        #    self._soft_delete_l3vpn_srv6_slicing_in_site(
        #        west_site, vn_name,
        #        obj_l3vpn_srv6_slicing.west_site_subnet_cidr,
        #        egress_node, node_type='egress')
        #except Exception as err:
        #    LOG.error(_LE("Failed delete L3VPN over SRv6 network "
        #                  "slicing[%(name)s], details %(err)s"),
        #              {'name': name, 'err': err})

        #    LOG.info(_LI("Update L3VPN over SRv6 network slicing "
        #                 "state to `inactive`."))
        #    obj_l3vpn_srv6_slicing.state = 'inactve'
        #    obj_l3vpn_srv6_slicing.save(context)
        #    return None

        obj_l3vpn_srv6_slicing.destroy(context)
