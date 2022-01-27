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

from jnpr.junos import Device
from jnpr.junos import exception as junos_exception
from jnpr.junos.utils.config import Config

from oslo_log import log

from dci.common import exception
from dci.common.i18n import _LE
from dci.common.i18n import _LI


LOG = log.getLogger(__name__)

EVPN_TYPE5_DCI_ROUTING_INSTANCE = 'DCI-EVPN-T5-RI-01'
FACE_TO_TF_ROUTING_INSTANCE = 'face-2-tf'
FACE_TO_DCI_ROUTING_INSTANCE = 'face-2-dci'


class Client(object):
    """MX client by Junos PyEZ.
    """

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def _get_configuration(self, dev, filter_xml):
        data = dev.rpc.get_config(options={'database': 'committed',
                                           'format': 'json'},
                                  filter_xml=filter_xml)
        return data

    def _edit_configuration(self, dev, cmd_list):
        with Config(dev) as cu:
            for cmd in cmd_list:
                cu.load(cmd, format='set')
            cu.pdiff()
            cu.commit()

    def configure_executor(self, mode, cmd_list=None, filter_xml=None):
        if not isinstance(mode, str) or mode not in ['ping', 'get', 'edit']:
            raise exception.InvalidParameterValue(
                err=("MX configure executor only support mode "
                     "[ping, get, edit], got [%s]") % mode)

        try:
            with Device(host=self.host,
                        port=self.port,
                        user=self.username,
                        password=self.password) as dev:

                if mode == 'ping' and not dev.connected:
                    raise exception.MXDeviceNotConnected(name=self.host)

                if mode == 'get':
                    if not filter_xml or not isinstance(filter_xml, str):
                        raise exception.InvalidParameterValue(
                            err=("configure_executor get mode only support "
                                 "filter xml string, got [%s]") % filter_xml)
                    else:
                        return self._get_configuration(dev, filter_xml)

                if mode == 'edit':
                    if not cmd_list or not isinstance(cmd_list, list):
                        raise exception.InvalidParameterValue(
                            err=("configure_executor edit mode only support "
                                 "commands list, got [%s]") % cmd_list)
                    else:
                        self._edit_configuration(dev, cmd_list)

        except junos_exception.ConnectError as err:
            LOG.error(_LE("Failed to connect to MX Device [%(name)s], "
                          "details %(err)s."),
                      {'name': self.host, 'err': err})
            raise err
        except junos_exception.CommitError as err:
            LOG.error(_LE("Failed to commit to MX Device [%(name)s], "
                          "details %(err)s"),
                      {'name': self.host, 'err': err})
            raise err
        except Exception as err:
            LOG.error(_LE("Failed to execute MX Device [%(name)s] "
                          "cmd list [%(cmds)s], details %(err)s"),
                      {'name': self.host, 'cmds': cmd_list, 'err': err})
            raise err

    def ping(self):
        self.configure_executor(mode='ping', cmd_list=[])

    def edit_l3evpn_dci_routing_instance_static_route(self, action,
                                                      subnet_cidr):
        cmd_list = []
        cmd_list.append('%(action)s routing-instances %(ri)s routing-options static route %(cidr)s discard' % {'action': action, 'ri': EVPN_TYPE5_DCI_ROUTING_INSTANCE, 'cidr': subnet_cidr})  # noqa
        self.configure_executor(mode='edit', cmd_list=cmd_list)

    def create_static_route(self, subnet_cidr):
        self.edit_l3evpn_dci_routing_instance_static_route(
            action='set', subnet_cidr=subnet_cidr)

    def retry_to_delete_static_route(self, subnet_cidr):
        retry = 3
        while retry:
            try:
                self.edit_l3evpn_dci_routing_instance_static_route(
                    action='delete', subnet_cidr=subnet_cidr)
                break
            except Exception as err:
                LOG.error(_LE("Failed to delete static route in MX, "
                              "retry count [-%(cnt)s], details %(err)s"),
                          {'cnt': retry, 'err': err})
                retry -= 1

    def edit_l2evpn_dci_routing_instance_bridge_domain(self, action, vn_name,
                                                       vn_vni, vn_route_target,
                                                       inter_vlan_id, dci_vni):
        cmd_list = []

        # Face To TF.
        cmd_list.append('%(action)s routing-instances %(ri)s protocols evpn vni-options vni %(vni)s vrf-target %(rt)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'vni': vn_vni, 'rt': vn_route_target})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'vni': vn_vni})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(inter_vlan_id)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'inter_vlan_id': inter_vlan_id})  # noqa
        cmd_list.append('%(action)s interfaces lt-0/0/10 unit 0 family bridge vlan-id-list %(inter_vlan_id)s' % {'action': action, 'inter_vlan_id': inter_vlan_id})  # noqa

        # Face To DCI.
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'vni': dci_vni})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(inter_vlan_id)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'inter_vlan_id': inter_vlan_id})  # noqa
        cmd_list.append('%(action)s interfaces lt-0/0/10 unit 1 family bridge vlan-id-list %(inter_vlan_id)s' % {'action': action, 'inter_vlan_id': inter_vlan_id})  # noqa
        self.configure_executor(mode='edit', cmd_list=cmd_list)

    def create_bridge_domain(self, vn_name, vn_vni, vn_route_target,
                             inter_vlan_id, dci_vni):
        self.edit_l2evpn_dci_routing_instance_bridge_domain(
            action='set',
            vn_name=vn_name,
            vn_vni=vn_vni,
            vn_route_target=vn_route_target,
            inter_vlan_id=inter_vlan_id,
            dci_vni=dci_vni)

    def retry_to_delete_bridge_domain(self, vn_name, vn_vni, vn_route_target,
                                      inter_vlan_id, dci_vni):
        retry = 3
        while retry:
            try:
                self.edit_l2evpn_dci_routing_instance_bridge_domain(
                    action='delete',
                    vn_name=vn_name,
                    vn_vni=vn_vni,
                    vn_route_target=vn_route_target,
                    inter_vlan_id=inter_vlan_id,
                    dci_vni=dci_vni)
                break
            except Exception as err:
                LOG.error(_LE("Failed to delete bridge domain in MX, "
                              "retry count [-%(cnt)s], details %(err)s"),
                          {'cnt': retry, 'err': err})
                retry -= 1

    def get_used_vid_and_vni_in_dci_bridge_domains(self):
        filter_xml = "<configuration><routing-instances><instance><name>%s</name><bridge-domains><domain/></bridge-domains></instance></routing-instances></configuration>" % FACE_TO_DCI_ROUTING_INSTANCE  # noqa
        inter_vlan_id_list = []
        dci_vni_list = []
        data = self.configure_executor(mode='get', filter_xml=filter_xml)
        domains = data['configuration']['routing-instances']['instance'][0]['bridge-domains']['domain']  # noqa
        for domain in domains:
            inter_vlan_id_list.append(domain['vlan-id'])
            dci_vni_list.append(domain['vxlan']['vni'])

        LOG.info(_LI("Get used inter_vlan_ids %(vid)s and dci_vnis %(vni)s"),
                 {'vid': inter_vlan_id_list, 'vni': dci_vni_list})
        return inter_vlan_id_list, dci_vni_list
