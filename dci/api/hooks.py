from oslo_config import cfg
from pecan import hooks


class ConfigHook(hooks.PecanHook):
    """Attach the config object to the request so controllers can get to it."""

    def before(self, state):
        state.request.cfg = cfg.CONF


class PublicUrlHook(hooks.PecanHook):
    """Attach the right public_url to the request.

    Attach the right public_url to the request so resources can create
    links even when the API service is behind a proxy or SSL terminator.
    """

    def before(self, state):
        state.request.public_url = (
            cfg.CONF.api.public_endpoint or state.request.host_url)
