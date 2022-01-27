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
    server = dci_service.WSGIService('dci-controller-api',
                                     CONF.api.enable_ssl_api)
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()
