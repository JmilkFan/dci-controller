import jinja2
import os

from netmiko import ConnectHandler
from oslo_log import log

from dci.common.i18n import _LE


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

    def _parse_output(self, output):
        """check the output of cmds.
        """

        if 'Error' in output:
            return False
        else:
            return True

    def executer(self, cmd):
        try:
            with ConnectHandler(**self.connection_info) as ssh_conn:
                output = ssh_conn.send_request(cmd)
        except Exception as err:
            LOG.error(_LE("Failed to execute SSH CLI cmd %(cmd)s, "
                          "details %(err)s"),
                      {'cmd': cmd, 'err': err})
            raise err

        return self._parse_output(output)

    def template_executer(self, file_name, kwargs={}):

        try:
            cmd = self._get_template_file_content(file_name).render(**kwargs)
        except Exception as err:
            LOG.error(_LE("Failed to get template file content of [%(file)s], "
                          "details %(err)s"),
                      {'file': file_name, 'err': err})
            raise err
        return self.executer(cmd)

    def ping_device(self):
        file_name = 'ping_device.jinja2'
        self.template_executer(file_name)
