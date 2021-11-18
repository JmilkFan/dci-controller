# Server Specific Configurations
# See https://pecan.readthedocs.org/en/latest/configuration.html#server-configuration # noqa
server = {
    'port': '6666',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
# See https://pecan.readthedocs.org/en/latest/configuration.html#application-configuration # noqa
app = {
    'root': 'dci.api.controllers.root.RootController',
    'modules': ['dci.api'],
    'static_root': '%(confdir)s/public',
    'debug': False,
    'acl_public_routes': [
        '/',
        '/v1'
    ]
}

# WSME Configurations
# See https://wsme.readthedocs.org/en/latest/integrate.html#configuration
wsme = {
    'debug': False
}
