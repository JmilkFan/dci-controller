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

    def __init__(self, device_conn_ref, *args, **kwargs):
        """Constructor of Device Manager.

        :param device_conn_ref:
            e.g.
            {
              "vendor": "huawei",
              "netconf_host": "192.168.30.2",
              "netconf_port": 22,
              "netconf_username": "usernmae",
              "netconf_password": "password",
            }
        """

        try:
            device_vendor = device_conn_ref['vendor']
            device_driver = DEVICE_DRIVER_MAPPING[device_vendor]
            self.driver_handle = importutils.import_object(
                device_driver,
                host=device_conn_ref['netconf_host'],
                port=device_conn_ref['netconf_port'],
                username=device_conn_ref['netconf_username'],
                password=device_conn_ref['netconf_password'])
        except Exception as err:
            LOG.error(_LE("Device driver instantiation failed, "
                          "details %s"), err)
            raise err

    def device_ping(self):
        try:
            self.driver_handle.liveness()
        except Exception as err:
            LOG.error(_LE("Failed to PING WAN Node NETCONF Server, "
                          "details %s"), err)
            raise err

    def test_netconf(self):
        return self.driver_handle.test_netconf()

    def create_evpn_vpls_over_srv6_be_vpn(self, vpn_configuration):
        return self.driver_handle.\
            create_evpn_vpls_over_srv6_be_vpn(**vpn_configuration)

    def delete_evpn_vpls_over_srv6_be_vpn(self, vpn_configuration):
        return self.driver_handle.\
            delete_evpn_vpls_over_srv6_be_vpn(**vpn_configuration)
