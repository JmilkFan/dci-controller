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
        xml_str = rpc_reply.data_xml
        if "<ok/>" in xml_str:
            print("Execute successfully.\n")
            return True
        else:
            print("Execute unccessfully\n.")
            return False

    def edit_config(self, config, target, error_option, is_locked=False):

        assert(":candidate" in self._handler.server_capabilities)
        assert(":validate" in self._handler.server_capabilities)

        if target != 'candidate':
            raise

        if error_option != 'rollback-on-error':
            raise

        if is_locked is False:
            raise

        with self._handler.locked(target='running'):
            self._handler.discard_changes()
            rpc_reply = self._handler.edit_config(
                config=config,
                target='candidate',
                default_operation='merge',
                test_option='test_then_set',
                error_option=error_option)

        if self._check_reply(rpc_reply):
            self._handler.validate(source='candidate')
            rpc_reply = self._handler.commit(confirmed=True)
        else:
            raise

        return rpc_reply
