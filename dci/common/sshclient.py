from oslo_log import log

from netmiko import ConnectHandler
import paramiko

from dci.common import exception
from dci.common.i18n import _LE


LOG = log.getLogger(__name__)


class SSHClient(object):
    def __init__(self, **kwargs):
        host = kwargs.get('host')
        port = kwargs.get('port')
        username = kwargs.get('username')
        password = kwargs.get('password', None)
        key_file = kwargs.get('key_file', None)

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if password:
            self.client.connect(hostname=host, port=port, username=username,
                                password=password)
        else:
            private = paramiko.RSAKey.from_private_key_file(key_file)
            self.client.connect(hostname=host, port=port, username=username,
                                pkey=private)

    def request(self, cli):
        stdin, stdout, stderr = self.client.exec_command(cli)
        result = stdout.read().decode('utf-8')
        return result


class NetworkDriverSSHClient(object):
    """Multi-vendor library to simplify Paramiko SSH connections to network
    devices.
    """

    def __init__(self, device_type, host, username, password, port=22,
                 secret='', use_keys=False, key_file=None):
        """Initialization of NetworkDriverSSHClient.

        :param host: Hostname of target device. Not required if `ip` is
                provided.
        :type host: str

        :param username: Username to authenticate against target device if
                required.
        :type username: str

        :param password: Password to authenticate against target device if
                required.
        :type password: str

        :param secret: The enable password if target device requires one.
        :type secret: str

        :param port: The destination port used to connect to the target
                device.
        :type port: int or None

        :param device_type: Class selection based on device type.
        :type device_type: str

        :param use_keys: Connect to target device using SSH keys.
        :type use_keys: bool

        :param key_file: Filename path of the SSH key file to use.
        :type key_file: str
        """

        connection_info = {}
        if not device_type:
            msg = _LE("Connection UPF , missed device_type!")
            LOG.error(msg)
            raise exception.InvalidAPIRequest(msg)
        if use_keys is True and key_file is None:
            msg = _LE("Connection UPF with user_key, missed key_file!")
            LOG.error(msg)
            raise exception.InvalidAPIRequest(msg)
        if use_keys is False:
            if not host or not username or not password:
                msg = _LE("Connection UPF with passwd, missed ipaddr, "
                          "username or passwd!")
                LOG.error(msg + device_type)
                raise exception.InvalidAPIRequest(msg)
        connection_info['device_type'] = device_type
        connection_info['host'] = host
        connection_info['username'] = username
        connection_info['password'] = password
        connection_info['port'] = port
        connection_info['secret'] = secret
        connection_info['use_keys'] = use_keys
        connection_info['key_file'] = key_file
        self.net_connect = ConnectHandler(**connection_info)

    def request(self, cli):
        output = self.net_connect.send_command(cli)
        self.net_connect.disconnect()
        return output
