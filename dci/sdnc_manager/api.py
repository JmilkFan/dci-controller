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

from dci.common.i18n import _LE
from dci.sdnc_manager.tungsten_fabric import vnc_api_client as tf_vnc_api


LOG = log.getLogger(__name__)


class SDNCManager(object):
    """Only support Tungsten Fabric SDN now.
    """

    def __init__(self, sdnc_conn_ref, *args, **kwargs):
        """Constructor of SDN-C Manager.

        :param sdnc_conn_ref:
            e.g.
            {
              "tf_api_server_host": "192.168.30.2",
              "tf_api_server_port": 8082,
              "tf_username": "admin",
              "tf_password": "password",
              "os_project_name": "admin"
            }
        """

        try:
            self.sdnc_handle = tf_vnc_api.Client(
                host=sdnc_conn_ref['tf_api_server_host'],
                port=sdnc_conn_ref['tf_api_server_port'],
                username=sdnc_conn_ref['tf_username'],
                password=sdnc_conn_ref['tf_password'],
                project=sdnc_conn_ref['os_project_name'])
        except Exception as err:
            LOG.error(_LE("SDN-C driver instantiation failed, "
                          "details %s"), err)
            raise err
