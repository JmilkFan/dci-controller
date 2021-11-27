import pecan

from jnpr.junos import Device
from jnpr.junos import exception as junos_exception
from jnpr.junos.utils.config import Config

from oslo_log import log

from dci.common.i18n import _LE
from dci import objects


LOG = log.getLogger(__name__)

EVPN_TYPE5_DCI_ROUTING_INSTANCE = 'DCI-EVPN-T5-RI-01'
FACE_TO_TF_ROUTING_INSTANCE = 'face-2-tf'
FACE_TO_DCI_ROUTING_INSTANCE = 'face-2-dci'


class Client(object):
    """MX client by Junos PyEZ.
    """

    @classmethod
    def edit_l3evpn_dci_routing_instance_static_route(cls, action,
                                                      site_uuid, subnet_cidr):
        context = pecan.request.context
        obj_site = objects.Site.get(context, site_uuid)

        cmd = '%(action)s routing-instances %(ri)s routing-options static route %(cidr)s discard' % {'action': action, 'ri': EVPN_TYPE5_DCI_ROUTING_INSTANCE, 'cidr': subnet_cidr}  # noqa

        try:
            with Device(host=obj_site.netconf_host,
                        port=obj_site.netconf_port,
                        user=obj_site.netconf_username,
                        password=obj_site.netconf_password) as dev:
                with Config(dev) as cu:
                    cu.load(cmd, format='set')
                    cu.pdiff()
                    cu.commit()
        except junos_exception.ConnectError as err:
            LOG.error(_LE("Failed to connect to MX Device [%(name)s], "
                          "details %(err)s."),
                      {'name': obj_site.netconf_host, 'err': err})
            raise err
        except junos_exception.CommitError as err:
            LOG.error(_LE("Failed to commit to MX Device [%(name)s], "
                          "details %(err)s"),
                      {'name': obj_site.netconf_host, 'err': err})
            raise err
        except Exception as err:
            LOG.error(_LE("Failed to edit[%(action)s] EVPN Type5 Static Route "
                          "for L3VPN DCI, details: %(err)s"),
                      {'action': action, 'err': err})
            raise err

    @classmethod
    def edit_l2evpn_dci_routing_instance_bridge_domain(cls, action, site_uuid,
                                                       vn_name, vn_vni,
                                                       vlan_id, route_target):
        context = pecan.request.context
        obj_site = objects.Site.get(context, site_uuid)

        route_target = 'target:' + route_target

        # Face To TF.
        cmd1 = '%(action)s routing-instances %(ri)s protocols evpn vni-options vni %(vni)s vrf-target %(rt)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'vni': vn_vni, 'rt': route_target}  # noqa
        cmd2 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name}  # noqa
        cmd3 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'vni': vn_vni}  # noqa
        cmd4 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(vlan_id)s' % {'action': action, 'ri': FACE_TO_TF_ROUTING_INSTANCE, 'bd': vn_name, 'vlan_id': vlan_id}  # noqa
        cmd5 = '%(action)s interfaces lt-0/0/10 unit 0 family bridge vlan-id-list %(vlan_id)s' % {'action': action, 'vlan_id': vlan_id}  # noqa

        # Face To DCI.
        cmd6 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s domain-type bridge' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name}  # noqa
        # TODO(fanguiju): Use exclusive DCI VNI ID.
        cmd7 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s vxlan vni %(vni)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'vni': '102400'}  # noqa
        cmd8 = '%(action)s routing-instances %(ri)s bridge-domains %(bd)s vlan-id %(vlan_id)s' % {'action': action, 'ri': FACE_TO_DCI_ROUTING_INSTANCE, 'bd': vn_name, 'vlan_id': vlan_id}  # noqa
        cmd9 = '%(action)s interfaces lt-0/0/10 unit 1 family bridge vlan-id-list %(vlan_id)s' % {'action': action, 'vlan_id': vlan_id}  # noqa

        try:
            with Device(host=obj_site.netconf_host,
                        port=obj_site.netconf_port,
                        user=obj_site.netconf_username,
                        password=obj_site.netconf_password) as dev:
                with Config(dev) as cu:
                    cu.load(cmd1, format='set')
                    cu.load(cmd2, format='set')
                    cu.load(cmd3, format='set')
                    cu.load(cmd4, format='set')
                    cu.load(cmd5, format='set')
                    cu.load(cmd6, format='set')
                    cu.load(cmd7, format='set')
                    cu.load(cmd8, format='set')
                    cu.load(cmd9, format='set')
                    cu.pdiff()
                    cu.commit()
        except junos_exception.ConnectError as err:
            LOG.error(_LE("Failed to connect to MX Device [%(name)s], "
                          "details %(err)s."),
                      {'name': obj_site.netconf_host, 'err': err})
            raise err
        except junos_exception.CommitError as err:
            LOG.error(_LE("Failed to commit to MX Device [%(name)s], "
                          "details %(err)s"),
                      {'name': obj_site.netconf_host, 'err': err})
            raise err
        except Exception as err:
            LOG.error(_LE("Failed to edit[%(action)s] EVPN Type5 Static Route "
                          "for L3VPN DCI, details: %(err)s"),
                      {'action': action, 'err': err})
            raise err
