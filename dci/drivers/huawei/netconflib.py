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

from dci.drivers.base_netconflib import BaseNETCONFLib

from dci.common import constants


class HuaweiNETCONFLib(BaseNETCONFLib):

    def __init__(self, host, port, username, password):
        super(HuaweiNETCONFLib, self).__init__(constants.HUAWEI, host, port,
                                               username, password)

    def _check_reply(self, rpc_reply):
        xml_str = rpc_reply.xml
        if "<ok/>" in xml_str:
            print("Execute successfully.\n")
            return True
        else:
            print("Execute unccessfully\n.")
            return False

    def edit_config(self, config, target, test_option, error_option, is_locked=True):  # noqa

        assert(":candidate" in self._client.server_capabilities)
        assert(":validate" in self._client.server_capabilities)

        if target != 'candidate':
            raise

        if error_option != 'rollback-on-error':
            raise

        if test_option != 'test-then-set':
            raise

        if is_locked is False:
            raise

        with self._client.locked(target='candidate'):

            self._client.discard_changes()
            rpc_reply = self._client.edit_config(
                config=config,
                target='candidate',
                default_operation='merge',
                test_option=test_option,
                error_option=error_option)

            if self._check_reply(rpc_reply):
                self._client.validate(source='candidate')
                rpc_reply = self._client.commit(confirmed=True)

            else:
                raise

        if not self._check_reply(rpc_reply):
            raise

        return None
