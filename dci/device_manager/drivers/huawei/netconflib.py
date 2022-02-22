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

from dci.common import constants
from dci.common.i18n import _LI
from dci.device_manager.drivers import base_netconflib

LOG = log.getLogger(__name__)


class HuaweiNETCONFLib(base_netconflib.BaseNETCONFLib):

    def __init__(self, host, port, username, password):
        super(HuaweiNETCONFLib, self).__init__(constants.HUAWEI, host, port,
                                               username, password)

    def _check_reply(self, rpc_reply):
        xml_str = rpc_reply.xml
        if "<ok/>" in xml_str:
            LOG.info(_LI("NETCONF Client edit-config execute successfully."))
            return True
        else:
            LOG.info(_LI("NETCONF Client edit-config execute unccessfully."))
            return False

    def edit_config(self, config, target, default_operation, test_option, error_option, is_locked=True):  # noqa

        if ":rollback-on-error" not in self._client.server_capabilities \
                or ":candidate" not in self._client.server_capabilities \
                or ":validate" not in self._client.server_capabilities:
            raise

        if target != 'candidate':
            raise

        if default_operation != 'merge':
            raise

        if test_option != 'test-then-set':
            raise

        if error_option != 'rollback-on-error':
            raise

        if is_locked is False:
            raise

        with self._client.locked(target='running'):

            self._client.discard_changes()
            rpc_reply = self._client.edit_config(
                config=config,
                target='candidate',
                default_operation='merge',
                test_option=test_option,
                error_option=error_option)

            if self._check_reply(rpc_reply):
                self._client.validate(source='candidate')
                rpc_reply = self._client.commit(confirmed=False)

            else:
                raise

        if not self._check_reply(rpc_reply):
            raise

        return None
