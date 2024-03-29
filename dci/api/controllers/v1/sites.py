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

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import link
from dci.api.controllers import types
from dci.api import expose
from dci.common import constants
from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci import objects
from dci.sdnc_manager.tungsten_fabric import vnc_api_client as tf_vnc_api


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

    name = types.text
    """The name of DCI site."""

    tf_api_server_host = types.ipv4
    """The Tungsten Fabric API Server IP address."""

    tf_api_server_port = types.integer
    """The Tungsten Fabric API Server Port."""

    tf_username = types.text
    """The Tungsten Fabric user."""

    tf_password = types.text
    """The Tungsten Fabric password."""

    os_auth_url = types.text
    """The Keystone Auth URL of OpenStack."""

    os_region = types.text
    """The Region of OpenStack."""

    os_project_domain_name = types.text
    """The Project Domain Name of OpenStack."""

    os_user_domain_name = types.text
    """The User Domain Name of OpenStack."""

    os_project_name = types.text
    """The Project of OpenStack."""

    os_username = types.text
    """The Username of OpenStack."""

    os_password = types.text
    """The Password of OpenStack."""

    state = types.text
    """State of DCI Site."""

    wan_nodes = types.list_of_dict
    """WAN Nodes associated to the site."""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        super(Site, self).__init__(**kwargs)
        self.fields = []
        for field in objects.Site.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, types.unset))

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

        try:
            tf_vnc_api.Client(host=site['tf_api_server_host'],
                              port=site['tf_api_server_port'],
                              username=site['tf_username'],
                              password=site['tf_password'],
                              project=site['os_project_name'])
        except Exception as err:
            LOG.error(_LE("Failed to PING Tungsten Fabric VNC API Server, "
                          "site login informations %s."), site)
            raise err

    @expose.expose(Site, types.text)
    def get_one(self, uuid):
        """Get a single Site by UUID.

        :param uuid: uuid of a Site.
        """
        LOG.info(_LI("[sites: get_one] UUID = (%s)"), uuid)
        context = pecan.request.context
        obj_site = objects.Site.get(context, uuid)
        return Site.convert_with_links(obj_site)

    @expose.expose(SiteCollection, types.text)
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

    @expose.expose(Site, body=Site, status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one Site.
        """
        req_body = req_body.as_dict()
        LOG.info(_LI("[sites: port] Request body = %s"), req_body)
        context = pecan.request.context

        req_body['os_project_name'] = req_body.get('os_project_name',
                                                   TF_DEFAULT_PROJECT)
        req_body['tf_api_server_port'] = req_body.get('tf_api_server_port',
                                                      TF_DEFAULT_PORT)
        self._ping_check(req_body)

        req_body['state'] = constants.ACTIVE
        obj_site = objects.Site(context, **req_body)
        obj_site.create(context)
        return Site.convert_with_links(obj_site)

    @expose.expose(Site, types.text, body=Site,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a Site.
        """
        req_body = req_body.as_dict()
        LOG.info("[sites: put] Request body = %s", req_body)
        context = pecan.request.context

        obj_site = objects.Site.get(context, uuid)
        for k, v in req_body.items():
            if getattr(obj_site, k) != v:
                setattr(obj_site, k, v)
        self._ping_check(obj_site.as_dict())

        obj_site.save(context)
        return Site.convert_with_links(obj_site)

    @expose.expose(None, types.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one Site by UUID.

        :param uuid: uuid of a Site.
        """
        context = pecan.request.context
        LOG.info('[site:delete] UUID = (%s)', uuid)
        obj_site = objects.Site.get(context, uuid)
        obj_site.destroy(context)
