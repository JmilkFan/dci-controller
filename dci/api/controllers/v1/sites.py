from http import HTTPStatus
import pecan
import wsme
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.juniper import mx_api
from dci.juniper import tf_vnc_api
from dci import objects


LOG = log.getLogger(__name__)
TF_DEFAULT_PROJECT = 'admin'
TF_DEFAULT_PORT = 8082
NETCONF_OVER_SSH_DEFAULT_PORT = 830


class Site(base.APIBase):
    """API representation of a DCI site.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation.
    """

    uuid = types.uuid
    """The UUID of the DCI site."""

    name = wtypes.text
    """The name of DCI site."""

    netconf_host = wtypes.IPv4AddressType()
    """The NETCONF host IP address."""

    netconf_port = wtypes.IntegerType()
    """The NETCONF host Port."""

    netconf_username = wtypes.text
    """The NETCONF user."""

    netconf_password = wtypes.text
    """The NETCONF password."""

    tf_api_server_host = wtypes.IPv4AddressType()
    """The Tungsten Fabric API Server IP address."""

    tf_api_server_port = wtypes.IntegerType()
    """The Tungsten Fabric API Server Port."""

    tf_username = wtypes.text
    """The Tungsten Fabric user."""

    tf_password = wtypes.text
    """The Tungsten Fabric password."""

    os_auth_url = wtypes.text
    """The Keystone Auth URL of OpenStack."""

    os_region = wtypes.text
    """The Region of OpenStack."""

    os_project_domain_name = wtypes.text
    """The Project Domain Name of OpenStack."""

    os_user_domain_name = wtypes.text
    """The User Domain Name of OpenStack."""

    os_project_name = wtypes.text
    """The Project of OpenStack."""

    os_username = wtypes.text
    """The Username of OpenStack."""

    os_password = wtypes.text
    """The Password of OpenStack."""

    state = wtypes.text
    """State of DCI Site."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(Site, self).__init__(**kwargs)
        self.fields = []
        for field in objects.Site.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_site):
        api_site = cls(**obj_site.as_dict())
        api_site.links = [
            link.Link.make_link('self', pecan.request.public_url,
                                'sites', api_site.uuid)
            ]
        return api_site


class SiteCollection(base.APIBase):
    """API representation of a collection of DCI sites."""

    sites = [Site]
    """A list containing Site objects"""

    @classmethod
    def convert_with_links(cls, sites):
        collection = cls()
        collection.sites = [Site.convert_with_links(site)
                            for site in sites]
        return collection


class SiteController(base.DCIController):
    """REST controller for DCI site Controller.
    """

    def _ping_check(self, site):
        # Ping TF VNC API
        try:
            tf_vnc_api.Client(site['tf_api_server_host'],
                              site['tf_api_server_port'],
                              site['tf_username'],
                              site['tf_password'],
                              site['os_project_name'])
        except Exception as err:
            # TODO(fanguiju): API response exception details and failure codes.
            LOG.error(_LE("Failed to PING Tungsten Fabric VNC API Server, "
                          "site login informations %s."), site)
            raise err

        # Ping MX NETCONF API
        try:
            mx_client = mx_api.Client(site['netconf_host'],
                                      site['netconf_port'],
                                      site['netconf_username'],
                                      site['netconf_password'])
            mx_client.ping()
        except Exception as err:
            LOG.error(_LE("Failed to PING MX NETCONF Server, "
                          "site login informations %s."), site)
            raise err

    @expose.expose(Site, wtypes.text)
    def get_one(self, uuid):
        """Get a single Site by UUID.

        :param uuid: uuid of a Site.
        """
        LOG.info(_LI("[sites: get_one] UUID = (%s)"), uuid)
        context = pecan.request.context
        obj_site = objects.Site.get(context, uuid)
        return Site.convert_with_links(obj_site)

    @expose.expose(SiteCollection, wtypes.text)
    def get_all(self, state=None):
        """Retrieve a list of Site.
        """
        filters_dict = {}
        if state:
            filters_dict['state'] = state

        LOG.info(_LI('[sites: get_all] filters = %s'), filters_dict)
        context = pecan.request.context
        obj_sites = objects.Site.list(context, filters=filters_dict)
        return SiteCollection.convert_with_links(obj_sites)

    @expose.expose(Site, body=types.jsontype, status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one Site.
        """
        LOG.info(_LI("[sites: port] Request body = %s"), req_body)
        context = pecan.request.context

        req_body['os_project_name'] = req_body.get('os_project_name',
                                                   TF_DEFAULT_PROJECT)
        req_body['tf_api_server_port'] = req_body.get('tf_api_server_port',
                                                      TF_DEFAULT_PORT)
        req_body['netconf_port'] = req_body.get('netconf_port',
                                                NETCONF_OVER_SSH_DEFAULT_PORT)
        self._ping_check(req_body)

        req_body['state'] = 'active'
        obj_site = objects.Site(context, **req_body)
        obj_site.create(context)
        return Site.convert_with_links(obj_site)

    @expose.expose(Site, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a Site.
        """
        LOG.info("[sites: put] Request body = %s", req_body)
        context = pecan.request.context

        obj_site = objects.Site.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_site, k) != v:
                setattr(obj_site, k, v)
        self._ping_check(obj_site.as_dict())

        obj_site.save(context)
        return Site.convert_with_links(obj_site)

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one Site by UUID.

        :param uuid: uuid of a Site.
        """
        context = pecan.request.context
        LOG.info('[site:delete] UUID = (%s)', uuid)
        obj_site = objects.Site.get(context, uuid)
        obj_site.destroy(context)
