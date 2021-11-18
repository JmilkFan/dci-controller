import inspect
import pecan
from pecan import rest
import wsme
from wsme import types as wtypes

API_V1 = 'v1'


class APIBase(wtypes.Base):

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return {k: getattr(self, k) for k in self.fields
                if hasattr(self, k) and getattr(self, k) != wsme.Unset}


class DCIController(rest.RestController):

    def _handle_patch(self, method, remainder, request=None):
        """Routes ``PATCH`` _custom_actions."""
        # route to a patch_all or get if no additional parts are available
        if not remainder or remainder == ['']:
            controller = self._find_controller('patch_all', 'patch')
            if controller:
                return controller, []
            pecan.abort(404)

        controller = getattr(self, remainder[0], None)
        if controller and not inspect.ismethod(controller):
            return pecan.routing.lookup_controller(controller, remainder[1:])
        # route to custom_action
        match = self._handle_custom_action(method, remainder, request)
        if match:
            return match

        # finally, check for the regular patch_one/patch requests
        controller = self._find_controller('patch_one', 'patch')
        if controller:
            return controller, remainder

        pecan.abort(405)
