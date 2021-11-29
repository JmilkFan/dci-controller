from jnpr.junos import Device
from jnpr.junos import exception as junos_exception
from jnpr.junos.utils.config import Config

from oslo_log import log

from dci.common import exception
from dci.common.i18n import _LE


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

    def executor(self, cmd_list):
        try:
            with Device(host=self.host,
                        port=self.port,
                        user=self.username,
                        password=self.password) as dev:
                if not dev.connected:
                    raise exception.MXDeviceNotConnected(name=self.host)
                if cmd_list and isinstance(cmd_list, list):
                    with Config(dev) as cu:
                        for cmd in cmd_list:
                            cu.load(cmd, format='set')
                        cu.pdiff()
                        cu.commit()
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
        self.executor(cmd_list=[])

    def edit_l3evpn_dci_routing_instance_static_route(self, action,
                                                      subnet_cidr):
        cmd_list = []
        cmd_list.append('%(action)s routing-instances %(ri)s routing-options static route %(cidr)s discard' % {'action': action, 'ri': EVPN_TYPE5_DCI_ROUTING_INSTANCE, 'cidr': subnet_cidr})  # noqa
        self.executor(cmd_list=cmd_list)

    def edit_l2evpn_dci_routing_instance_bridge_domain(self, action,
                                                       vn_name, vn_vni,
                                                       vlan_id, route_target):
        cmd_list = []

        # Face To TF.
        route_target = 'target:' + route_target
        cmd_list.append('%(action)s routing-instances %(ri)s protocols evpn vni-options vni %(vni)s vrf-target %(rt)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'vni': vn_vni, 'rt': route_target})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'vni': vn_vni})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(vlan_id)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'vlan_id': vlan_id})  # noqa
        cmd_list.append('%(action)s interfaces lt-0/0/10 unit 0 family bridge vlan-id-list %(vlan_id)s' % {'action': action, 'vlan_id': vlan_id})  # noqa

        # Face To DCI.
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'vni': '102400'})  # noqa
        cmd_list.append('%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(vlan_id)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'vlan_id': vlan_id})  # noqa
        cmd_list.append('%(action)s interfaces lt-0/0/10 unit 1 family bridge vlan-id-list %(vlan_id)s' % {'action': action, 'vlan_id': vlan_id})  # noqa
        self.executor(cmd_list=cmd_list)
