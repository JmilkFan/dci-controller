import json
from webob import exc

from oslo_log import log

from dci.api.controllers import base
from dci.api.controllers import types
from dci.api import expose
from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI


LOG = log.getLogger(__name__)


class DCIController(base.dcioreController):
    """REST controller for DCI Controller
    """

    @expose.expose(types.jsontype, body=types.jsontype, status_code=200)
    def post(self, req_body):
        pass
