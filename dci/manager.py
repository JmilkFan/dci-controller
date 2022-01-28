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

from oslo_log import log
from oslo_utils import importutils

from dci.common.i18n import _LE


LOG = log.getLogger(__name__)


DEVICE_DRIVER_MAPPING = {
    'huawei': 'dci.drivers.huawei.netengine.NetEngineDriver',
    # TODO(fanguiju): Juniper devices are not supported.
    'juniper': 'dci.drivers.juniper.junos.JunosDriver'
}


class DCIManager(object):

    def __init__(self, device_vendor, host, port, username, password):
        """Load the driver from the one specified in args, or from flags."""

        device_driver = DEVICE_DRIVER_MAPPING[device_vendor]
        self.driver = importutils.import_object(device_driver,
                                                device_vendor=device_vendor,
                                                host=host,
                                                port=port,
                                                username=username,
                                                password=password)

    def netconf_ping(self):
        try:
            self.driver.liveness()
        except Exception as err:
            LOG.error(_LE("Failed to PING WAN Node NETCONF Server, "
                          "details %s"), err)
            raise err

    def create_vpls_over_srv6_be_l2vpn_slicing(self):
        pass
