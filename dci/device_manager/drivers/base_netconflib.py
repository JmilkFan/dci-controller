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

from ncclient import manager
from ncclient.operations import errors as nccli_oper_excepts
from ncclient.transport import errors as nccli_trans_excepts

import lxml.etree as ET
import xmltodict

from dci.common import constants
from dci.common.i18n import _LI


LOG = log.getLogger(__name__)


class NETCONFParser(object):
    """NETCONF Utility Class.
    """

    def __init__(self, rpc_command):

        if isinstance(rpc_command, str) or isinstance(rpc_command, bytes):
            self.rpc_command = ET.fromstring(
                rpc_command,
                parser=ET.XMLParser(recover=False,
                                    remove_blank_text=True))
        else:
            self.rpc_command = rpc_command

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,
                           self.rpc_command.__class__.__name__)

    def __str__(self):
        return ET.tostring(self.rpc_command, pretty_print=True)

    def get_namespace(self):
        """Return NETCONF version namespace.
        """
        if self.rpc_command.tag.startswith('{'):
            return self.rpc_command.tag.split('}')[0].split('{')[1]

    def get_operation(self):
        """Return NETCONF operation from rpc command.
        """
        return NETCONFParser._get_tag(self.rpc_command[0])

    def get_datastore(self):
        """Return NETCONF target datastore from rpc command.
        """
        op = self.get_operation()
        ns = self.get_namespace()
        if op == 'edit-config':
            target = self.rpc_command.find('{%s}edit-config/{%s}target' % (ns, ns))  # noqa
            return NETCONFParser._get_tag(target[0])
        if op == 'get-config':
            source = self.rpc_command.find('{%s}get-config/{%s}source' % (ns, ns))  # noqa
            return NETCONFParser._get_tag(source[0])
        return None

    def get_default_operation(self):
        """Return NETCONF error_option from rpc command.
        """
        op = self.get_operation()
        ns = self.get_namespace()
        if op == 'edit-config':
            option = self.rpc_command.find('{%s}edit-config/{%s}default-operation' % (ns, ns))  # noqa
            if option is not None:
                return option.text
        return None

    def get_error_option(self):
        """Return NETCONF error_option from rpc command.
        """
        op = self.get_operation()
        ns = self.get_namespace()
        if op == 'edit-config':
            option = self.rpc_command.find('{%s}edit-config/{%s}error-option' % (ns, ns))  # noqa
            if option is not None:
                return option.text
        return None

    def get_test_option(self):
        """Return NETCONF test_option from rpc command.
        """
        op = self.get_operation()
        ns = self.get_namespace()
        if op == 'edit-config':
            option = self.rpc_command.find('{%s}edit-config/{%s}test-option' % (ns, ns))  # noqa
            if option is not None:
                return option.text
        return None

    def get_data(self):
        """Return NETCONF RPC request data from rpc command
        """
        op = self.get_operation()
        ns = self.get_namespace()
        if op in ['edit-config']:
            return self.rpc_command.find('{%s}edit-config/{%s}config' % (ns, ns))  # noqa
        if op in ['get-config']:
            return self.rpc_command.find('{%s}get-config/{%s}filter' % (ns, ns))  # noqa
        if op in ['get']:
            return self.rpc_command.find('{%s}get/{%s}filter' % (ns, ns))
        return self.rpc_command[0]

    @staticmethod
    def _get_tag(elem):
        if elem.tag.startswith('{'):
            return elem.tag.split('}')[1]
        return elem.tag


class BaseNETCONFLib(object):

    def __init__(self, vendor, host, port, username, password):

        self.vendor = vendor
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._client = None

    def connect(self):
        if not self._client or not self._client.connected:
            link_device_params = {
                'host': self.host,
                'port': self.port,
                'username': self.username,
                'password': self.password,
                'timeout': 120,
                'allow_agent': False,
                'look_for_keys': False,
                'hostkey_verify': False,
                'device_params': {'name': constants.DEVICE_VENDOR_MAPPING[self.vendor]}  # noqa
            }
            LOG.info(_LI("Connect to device [%s] by ncclient."), self.host)
            try:
                self._client = manager.connect(**link_device_params)
            except nccli_trans_excepts.AuthenticationError as err:
                raise err
            except Exception as err:
                raise err

    def disconnect(self):
        if self._client.connected:
            LOG.info(_LI("Disconnect to device [%s] by ncclient."), self.host)
            try:
                self._client.close_session()
            except Exception as err:
                raise err
        self._client = None

    def _execute(self, rpc_op, rpc_db, rpc_req_data,
                 def_oper, test_option, err_option, lock):

        # NOTE(fanguiju): Use the `ncclient.manager.connect` Context Manager.
        with self._client:
            try:
                if rpc_op == 'get':
                    rpc_reply = self._client.get(
                        filter=rpc_req_data)

                elif rpc_op == 'get-config':
                    rpc_reply = self._client.get_config(
                        source=rpc_db,
                        filter=rpc_req_data)

                elif rpc_op == 'edit-config':
                    rpc_reply = self.edit_config(config=rpc_req_data,
                                                 target=rpc_db,
                                                 default_operation=def_oper,
                                                 test_option=test_option,
                                                 error_option=err_option,
                                                 is_locked=lock)
                else:
                    rpc_reply = self._client.dispatch(ET.fromstring(rpc_req_data))  # noqa
            except nccli_trans_excepts.TransportError as err:
                raise err
            except nccli_oper_excepts.TimeoutExpiredError as err:
                raise err
            except Exception as err:
                raise err
        return rpc_reply

    def edit_config(self, config, target, error_option, is_locked=True):
        # NOTE(fanguiju): Implemented by device driver.
        raise NotImplementedError()

    def executor(self, rpc_command, lock=True, result_format='xml'):
        """NETCONF executor.

        :param rpc_command: xmlstring.
        """

        parser = NETCONFParser(rpc_command)
        rpc_op = parser.get_operation()
        rpc_db = parser.get_datastore()
        def_oper = parser.get_default_operation()
        test_option = parser.get_test_option()
        err_option = parser.get_error_option()

        if parser.get_data():
            rpc_req_data = ET.tostring(parser.get_data(), pretty_print=True)
            if isinstance(rpc_req_data, bytes):
                rpc_req_data = rpc_req_data.decode('UTF-8')
        else:
            rpc_req_data = None

        rpc_reply = self._execute(rpc_op, rpc_db, rpc_req_data,
                                  def_oper, test_option, err_option, lock)

        if rpc_reply:
            return self._return_result(rpc_reply, result_format)
        else:
            return None

    def _return_result(self, rpc_reply, result_format):

        if result_format == 'xml':
            data = ET.fromstring(rpc_reply.data_xml.encode())
            return ET.tostring(data).decode()

        elif result_format == 'dict':
            return xmltodict.parse(rpc_reply.data_xml)

        elif result_format == 'raw':
            return rpc_reply

        else:
            raise

    def get_server_capabilities(self):
        return self._client.server_capabilities
