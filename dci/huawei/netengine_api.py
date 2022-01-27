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

import jinja2
import os

from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException

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
            'secret': secret,  # enable password
            'use_keys': use_keys,
            'key_file': key_file,
            'session_log': '/tmp/netmiko_session_log.txt'
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
        if isinstance(outputs, str):
            if 'Error' in outputs:
                raise exception.SSHCLIExecutionError()
            else:
                return True

        elif isinstance(outputs, list):
            for output in outputs:
                if 'Error' in output:
                    raise exception.SSHCLIExecutionError()
            else:
                return True

        elif isinstance(outputs, dict):
            for _, v in outputs.items():
                if 'Error' in v:
                    raise exception.SSHCLIExecutionError()
            else:
                return True

        else:
            pass

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
                if self.connection_info['secret']:
                    ssh_conn.enable()

                outputs = ssh_conn.send_config_set(cmd_list,
                                                   strip_prompt=False,
                                                   strip_command=False,
                                                   delay_factor=5)
                outputs += ssh_conn.save_config()
        except NetmikoTimeoutException as err:
            LOG.error(_LE("Failed to send commands to device %s, "
                          "connect time out..."), self.connection_info['host'])
            raise err
        except NetmikoAuthenticationException as err:
            LOG.error(_LE("Failed to send commands to device %s, "
                          "authentication failed."))
            raise err
        except Exception as err:
            LOG.error(_LE("Failed to send config set to device %(host)s, "
                          "details %(err)s"),
                      {'host': self.connection_info['host'], 'err': err})
            raise err

        LOG.info(_LI("""
==============================================
Outputs:

%(outputs)s
==============================================
                     """), {'outputs': outputs})

        self._parse_outputs(outputs)

    def send_commands(self, cmds=[]):

        LOG.info(_LI("SSHCLI send commands to device [%(host)s]: %(cmds)s"),
                 {'host': self.connection_info['host'], 'cmds': cmds})

        try:
            with ConnectHandler(**self.connection_info) as ssh_conn:
                if self.connection_info['secret']:
                    ssh_conn.enable()

                outputs = {}
                for cmd in cmds:
                    outputs[cmd] = ssh_conn.send_command(cmd)

        except NetmikoTimeoutException as err:
            LOG.error(_LE("Failed to send commands to device %s, "
                          "connect time out..."), self.connection_info['host'])
            raise err
        except NetmikoAuthenticationException as err:
            LOG.error(_LE("Failed to send commands to device %s, "
                          "authentication failed."))
            raise err
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

    def setup_node_for_l3vpn_srv6_be_slicing(self, action, kwargs):
        file_name = 'setup_node_for_l3vpn_srv6_be_slicing.jinjia2'
        kwargs['action'] = action
        self.send_config_set_from_template(file_name, kwargs)
