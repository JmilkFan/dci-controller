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
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.huawei import netengine_api
from dci import objects


LOG = log.getLogger(__name__)


class WANNode(base.APIBase):
    """API representation of a WAN node.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the WAN node."""

    name = wtypes.text
    """The name of WAN node."""

    vendor = wtypes.text
    """Network Device Vendor."""

    conn_type = wtypes.text
    """Type of connect to device."""

    ssh_host = wtypes.IPv4AddressType()
    """The SSHCLI host IP address."""

    ssh_port = wtypes.IntegerType()
    """The SSHCLI host Port."""

    ssh_username = wtypes.text
    """The SSHCLI user."""

    ssh_password = wtypes.text
    """The SSHCLI password."""

    state = wtypes.text
    """State of WANNode."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(WANNode, self).__init__(**kwargs)
        self.fields = []
        for field in objects.WANNode.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_wan_node):
        api_wan_node = cls(**obj_wan_node.as_dict())
        api_wan_node.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'wan_nodes', api_wan_node.uuid)
            ]
        return api_wan_node


class WANNodeCollection(base.APIBase):
    """API representation of a collection of WAN nodes."""

    wan_nodes = [WANNode]
    """A list containing WANNode objects"""

    @classmethod
    def convert_with_links(cls, wan_nodes):
        collection = cls()
        collection.wan_nodes = [WANNode.convert_with_links(wan_node)
                                for wan_node in wan_nodes]
        return collection


class WANNodeController(base.DCIController):
    """REST controller for WAN node Controller.
    """

    def _ping_check(self, wan_node):

        # Ping WAN Node SSHCLI API
        try:
            ssh_client = netengine_api.Client(
                host=wan_node['ssh_host'],
                port=wan_node['ssh_port'],
                username=wan_node['ssh_username'],
                password=wan_node['ssh_password'])
            ssh_client.ping_device()
        except Exception as err:
            LOG.error(_LE("Failed to PING WAN Node SSHCLI Server, "
                          "wan_node login informations %s."), wan_node)
            raise err

    @expose.expose(WANNode, wtypes.text)
    def get_one(self, uuid):
        """Get a single WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        LOG.info(_LI("[wan_nodes: get_one] UUID = (%s)"), uuid)
        context = pecan.request.context
        obj_wan_node = objects.WANNode.get(context, uuid)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNodeCollection, wtypes.text)
    def get_all(self, state=None):
        """Retrieve a list of WANNode.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state

        LOG.info(_LI('[wan_nodes: get_all] filters = %s'), filters_dict)
        context = pecan.request.context
        obj_wan_nodes = objects.WANNode.list(context, filters=filters_dict)
        return WANNodeCollection.convert_with_links(obj_wan_nodes)

    @expose.expose(WANNode, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one WANNode.
        """
        LOG.info(_LI("[wan_nodes: port] Request body = %s"), req_body)
        context = pecan.request.context

        self._ping_check(req_body)

        req_body['vendor'] = constants.HUAWEI
        req_body['conn_type'] = constants.SSHCLI
        req_body['state'] = constants.ACTIVE
        obj_wan_node = objects.WANNode(context, **req_body)
        obj_wan_node.create(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(WANNode, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a WANNode.
        """
        LOG.info("[wan_nodes: put] Request body = %s", req_body)
        context = pecan.request.context

        obj_wan_node = objects.WANNode.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_wan_node, k) != v:
                setattr(obj_wan_node, k, v)

        self._ping_check(obj_wan_node.as_dict())

        obj_wan_node.save(context)
        return WANNode.convert_with_links(obj_wan_node)

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one WANNode by UUID.

        :param uuid: uuid of a WANNode.
        """
        context = pecan.request.context
        LOG.info('[wan_node: delete] UUID = (%s)', uuid)
        obj_wan_node = objects.WANNode.get(context, uuid)
        obj_wan_node.destroy(context)
