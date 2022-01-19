from ncclient import manager
from ncclient.transport import errors as ncclient_exceptions

import lxml.etree as ET
import xml
import xmltodict

from dci.common import constants
from dci.common.i18n import _LE


class NETCONFParser(object):
    """NETCONF Utility Class.
    """

    def __init__(self, rpc_command):

        if isinstance(rpc_command, str):
            self.rpc_command = ET.fromstring(
                rpc_command,
                parser=ET.XMLParser(remove_blank_text=True))
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

    def __init__(self, host, port, username, password, vendor):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vendor = vendor
        self._handler = None

    def __enter__(self):

        try:
            vendor_str = constants.DEVICE_VENDOR_MAPPING[self.vendor]
        except Exception as err:
            raise err

        link_device_params = {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'timeout': 60,
            'allow_agent': False,
            'look_for_keys': False,
            'hostkey_verify': False,
            'device_params': {'name': vendor_str}
        }

        try:
            self._handler = manager.connect(**link_device_params)
        except ncclient_exceptions.AuthenticationError as err:
            raise err
        except Exception as err:
            raise err

    def __exit__(self, exc_ty, exc_val, tb):
        self._handler.close_session()

    def _check_reply(self, rpc_reply):
        xml_str = rpc_reply.data_xml
        if "<ok/>" in xml_str:
            print("Execute successfully.\n")
            return True
        else:
            print("Execute unccessfully\n.")
            return False

    def _huawei_edit_config(self, config, target, error_option, is_locked):
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

    def _edit_config(self, config, target, error_option, is_locked=False):

        if self.vendor == constants.HUAWEI:
            rpc_reply = self._huawei_edit_config(
                config, target, error_option, is_locked)

        elif self.vendor == constants.JUNIPER:
            err_msg = _LE("Juniper devices are not supported")
            raise NotImplementedError(err_msg)

        else:
            raise

        return rpc_reply

    def executor(self, rpc_command, lock=False, result_format='xml'):

        parser = NETCONFParser(rpc_command)
        rpc_op = parser.get_operation()
        rpc_db = parser.get_datastore()
        rpc_req_data = ET.tostring(parser.get_data(), pretty_print=True)

        try:
            if rpc_op == 'get':
                rpc_reply = self._handler.get(
                    filter=('subtree', rpc_req_data))

            elif rpc_op == 'get-config':
                rpc_reply = self._handler.get_config(
                    source=rpc_db,
                    filter=('subtree', rpc_req_data))

            elif rpc_op == 'edit-config':
                err_option = parser.get_error_option()
                rpc_reply = self._edit_config(config=rpc_req_data,
                                              target=rpc_db,
                                              error_option=err_option,
                                              is_locked=lock)
            else:
                rpc_reply = self._handler.dispatch(ET.fromstring(rpc_req_data))
        except ncclient_exceptions.TimeoutExpiredError as err:
            raise err
        except ncclient_exceptions.TransportError as err:
            raise err
        except Exception as err:
            raise err

        if result_format == 'xml':
            return xml.dom.minidom.parseString(rpc_reply.data_xml).toprettyxml()  # noqa
        elif result_format == 'dict':
            return xmltodict.parse(rpc_reply.data_xml)
        elif result_format == 'raw':
            return rpc_reply
        else:
            raise

    def get_server_capabilities(self):
        return self._handler.server_capabilities
