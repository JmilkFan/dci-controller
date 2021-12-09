import jinja2
import os

from netmiko import ConnectHandler
from oslo_log import log

from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI


LOG = log.getLogger(__name__)


class Client(object):
    """NetEngine client by netmiko.
    """

    def __init__(self, host, username, password, port=22,
                 secret='', use_keys=False, key_file=None):

        self.connection_info = {
            'device_type': 'huawei',
            'host': host,
            'username': username,
            'password': password,
            'port': port,
            'secret': secret,
            'use_keys': use_keys,
            'key_file': key_file
        }

    def _get_template_file_content(self, file_name):
        """Returns the specified Jinja configuration template.
        """
        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         'templates/%s' % file_name))

        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.dirname(file_path))
        jinja_env = jinja2.Environment(autoescape=True,
                                       loader=template_loader,
                                       trim_blocks=True,
                                       lstrip_blocks=True)

        return jinja_env.get_template(os.path.basename(file_path))

    def _parse_outputs(self, outputs):
        """check the outputs from device return.
        """
        for output in outputs:
            if 'Error' in output:
                raise exception.SSHCLIExecutionRrror(outputs=outputs)
        else:
            return True

    def send_config_set_from_template(self, file_name, kwargs={}):
        try:
            cmd_str = self._get_template_file_content(
                file_name).render(**kwargs)
        except Exception as err:
            LOG.error(_LE("Failed to get template file content of [%(file)s], "
                          "details %(err)s"),
                      {'file': file_name, 'err': err})
            raise err

        LOG.info(_LI("""
==============================================
SSHCLI send config set to device [%(host)s]:

%(cmds)s
==============================================
                     """), {'host': self.connection_info['host'],
                            'cmds': cmd_str})

        cmd_list = cmd_str.split('\n')
        try:
            with ConnectHandler(**self.connection_info) as ssh_conn:
                outputs = ssh_conn.send_config_set(cmd_list, delay_factor=0.2)
                outputs += ssh_conn.save_config()
        except Exception as err:
            LOG.error(_LE("Failed to send config set to device %(host)s, "
                          "details %(err)s"),
                      {'host': self.connection_info['host'], 'err': err})
            raise err

        self._parse_outputs(outputs)

    def send_commands(self, cmds=[]):

        LOG.info(_LI("SSHCLI send commands to device [%(host)s]: %(cmds)s"),
                 {'host': self.connection_info['host'], 'cmds': cmds})

        try:
            with ConnectHandler(**self.connection_info) as ssh_conn:
                outputs = []
                for cmd in cmds:
                    output = ssh_conn.send_command(cmd)
                    outputs.append(output)
        except Exception as err:
            LOG.error(_LE("Failed to send commands to device %(host)s, "
                          "details %(err)s"),
                      {'host': self.connection_info['host'], 'err': err})
            raise err

        LOG.info(_LI("SSHCLI outputs from commands %s"), outputs)
        self._parse_outputs(outputs)

    def ping_device(self):
        cmds = ['display this']
        self.send_commands(cmds)
