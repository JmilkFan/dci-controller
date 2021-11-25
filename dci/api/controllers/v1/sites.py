import pecan
import json
from http import HTTPStatus
from webob import exc
from wsme import types as wtypes

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import types
from dci.api import expose
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci import objects
from dci.api.controllers import link


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

    netconf_host = wtypes.text
    """The NETCONF host IP address."""

    netconf_username = wtypes.text
    """The NETCONF user."""

    netconf_password = wtypes.text
    """The NETCONF password."""

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
    def get_all(self, state):
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
        obj_site = objects.Site.create(context, req_body)
        return Site.convert_with_links(obj_site)

    @expose.expose(Site, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a Site.
        """
        LOG.info("[sites:put] Req = (%s)", req_body)
        context = pecan.request.context
        obj_site = objects.Site.save(context, uuid, req_body)
        return Site.convert_with_links(obj_site)

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one Site by UUID.

        :param uuid: uuid of a Site.
        """
        context = pecan.request.context
        LOG.info('[site:delete] UUID = (%s)', uuid)
        objects.Site.destory(context, uuid)
