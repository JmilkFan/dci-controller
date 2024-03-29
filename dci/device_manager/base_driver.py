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

"""Device Drivers for networking."""


import abc


class BaseDeviceDriver(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def liveness(self):
        """Connectivity check of network device.
        """
        return

    @abc.abstractmethod
    def test_netconf(self):
        return


class SRv6VPNDeviceDriver(object, metaclass=abc.ABCMeta):
    pass


class DeviceDriver(SRv6VPNDeviceDriver, BaseDeviceDriver):
    pass
