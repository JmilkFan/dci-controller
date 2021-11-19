import json
from http import HTTPStatus
from webob import exc

from oslo_log import log
from wsme import types as wtypes

from dci.api.controllers import base
from dci.api.controllers import types
from dci.api import expose
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI


LOG = log.getLogger(__name__)


class L3VPNController(base.DCIController):
    """REST controller for L3 VPN Controller.
    """

    @expose.expose(types.jsontype, wtypes.text)
    def get_one(self, uuid):
        """Get a single L3VPN by UUID.

        :param uuid: uuid of a L3VPN.
        """
        return {'get_one': uuid}

    @expose.expose(types.jsontype)
    def get_all(self):
        """Retrieve a list of L3VPN.
        """
        return {'get_all': 'all'}

    @expose.expose(types.jsontype, body=types.jsontype,
                   status_code=HTTPStatus.CREATED)
    def post(self, req_body):
        """Create one L3VPN.
        """
        return {'post': req_body}

    @expose.expose(types.jsontype, wtypes.text, body=types.jsontype,
                   status_code=HTTPStatus.ACCEPTED)
    def put(self, uuid, req_body):
        """Update a L3VPN.
        """
        return {'uuid': uuid, 'put': req_body}

    @expose.expose(None, wtypes.text, status_code=HTTPStatus.NO_CONTENT)
    def delete(self, uuid):
        """Delete one L3VPN by UUID.

        :param uuid: uuid of a L3VPN.
        """
        return None
