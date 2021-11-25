import pecan
from pecan import rest
from wsme import types as wtypes

from dci.api.controllers import base
from dci.api.controllers import v1
from dci.api import expose


class Root(base.APIBase):
    name = wtypes.text
    """The name of the API"""

    description = wtypes.text
    """Some information about this API"""

    @staticmethod
    def convert():
        root = Root()
        root.name = 'DCI Controller API'
        root.description = ('DCI Controller')
        return root


class RootController(rest.RestController):
    _versions = [base.API_V1]
    """All supported API versions"""

    _default_version = base.API_V1
    """The default API version"""

    v1 = v1.Controller()

    @expose.expose(Root)
    def get(self):
        return Root.convert()

    @pecan.expose()
    def _route(self, args, request=None):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the dci-controller API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)
