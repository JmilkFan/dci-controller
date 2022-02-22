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
    'huawei': 'dci.device_manager.drivers.huawei.netengine.NetEngineDriver',
    # TODO(fanguiju): Juniper devices are not supported.
    'juniper': 'dci.device_manager.drivers.juniper.junos.JunosDriver'
}


class DeviceManager(object):

    def __init__(self, device_connection_info, *args, **kwargs):
        """Constructor of WAN Manager.

        :param device_connection_info:
            e.g.
            {
              "vendor": "huawei",
              "netconf_host": "192.168.30.2",
              "netconf_port": 22,
              "netconf_username": "yunshan",
              "netconf_password": "Huawei@123",
            }
        """

        self.device_handle = None
        self._instantiate_wan_manager_handle(device_connection_info)

    def _instantiate_wan_manager_handle(self, device_connection_info):
        if not self.device_handle:
            try:
                device_vendor = device_connection_info['vendor']
                device_driver = DEVICE_DRIVER_MAPPING[device_vendor]
                self.driver_handle = importutils.import_object(
                    device_driver,
                    host=device_connection_info['netconf_host'],
                    port=device_connection_info['netconf_port'],
                    username=device_connection_info['netconf_username'],
                    password=device_connection_info['netconf_password'])
            except Exception as err:
                LOG.error(_LE("Device driver instantiation failed, "
                              "details %s"), err)
                raise

    def device_ping(self):
        try:
            self.driver_handle.liveness()
        except Exception as err:
            LOG.error(_LE("Failed to PING WAN Node NETCONF Server, "
                          "details %s"), err)
            raise err

    def create_an_and_wan_evpn_vpls_over_srv6_be(self):
        pass

    def test_netconf(self):
        return self.driver_handle.test_netconf()


class DCIManager(DeviceManager):

    def create_wan_evpn_vpls_over_srv6_be(self):
        pass


class DCAManager(DeviceManager):

    def create_an_evpn_vxlan(self):
        pass


class DCNManager(object):

    def __init__(self, sdnc_connection_info, *args, **kwargs):
        self.sdnc_handle = None
        self._instantiate_dcn_manager_handle(sdnc_connection_info)

    def _instantiate_dcn_manager_handle(self, sdnc_connection_info):
        if not self.sdnc_handle:
            pass

    def create_vn_evpn_vxlan(self):
        pass


class NetworkSlicingManager(DCNManager, DCAManager, DCIManager):

    def __init__(self, device_connection_info, sdnc_connection_info, *args, **kwargs):  # noqa
        """Load the driver from the one specified in args, or from flags.

        :param device_connection_info: Connect to Router Device of WAN.
        :param sdnc_connection_info: Connect to SDN Controller of DCN.
        """
        super(DCIManager, self).__init__(
            device_connection_info=device_connection_info,
            sdnc_connection_info=sdnc_connection_info,
            *args, **kwargs)

    def create_vpls_over_srv6_be_l2vpn_slicing(self):
        pass
