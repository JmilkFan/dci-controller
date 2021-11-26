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


LOG = log.getLogger(__name__)


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

    tf_project_uuid = types.uuid
    """The UUID of the Tungsten Fabric Project."""

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

    @expose.expose(Site, wtypes.text)
    def get_one(self, uuid):
        """Get a single Site by UUID.

        :param uuid: uuid of a Site.
        """
        LOG.info("[sites:get_one] UUID = (%s)", uuid)
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
        context = pecan.request.context
        obj_sites = objects.Site.list(context, filters=filters_dict)
        LOG.info('[sites:get_all] Returned: %s', obj_sites)
        return SiteCollection.convert_with_links(obj_sites)

    @expose.expose(Site, body=types.jsontype, status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one Site.
        """
        LOG.info("[sites:port] Req = (%s)", req_body)
        context = pecan.request.context

        # TODO(fanguiju): Get DCI site state through health check mechanism,
        #                 default state is `active`.
        req_body['state'] = 'active'
        obj_site = objects.Site(context, **req_body)
        obj_site.create(context)
        return Site.convert_with_links(obj_site)

    @expose.expose(Site, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a Site.
        """
        LOG.info("[sites:put] Req = (%s)", req_body)
        context = pecan.request.context

        obj_site = objects.Site.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_site, k) != v:
                setattr(obj_site, k, v)
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
