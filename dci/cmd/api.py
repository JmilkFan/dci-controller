"""The DCI Controller API."""

import sys

from oslo_config import cfg

from dci.common import service as dci_service


CONF = cfg.CONF


def main():
    # Parse config file and command line options, then start logging
    dci_service.prepare_service(sys.argv)

    # Build and start the WSGI app
    launcher = dci_service.process_launcher()
    server = dci_service.WSGIService('dci_controller_api',
                                     CONF.api.enable_ssl_api)
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()
