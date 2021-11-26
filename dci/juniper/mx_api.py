import pecan

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos import exception as junos_exception

from oslo_log import log

from dci.common.i18n import _LE
from dci import objects


LOG = log.getLogger(__name__)

EVPN_TYPE5_DCI_ROUTING_INSTANCE = 'DCI-EVPN-T5-RI-01'


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
        except junos_exception.CommitError as err:
            LOG.error(_LE("Failed to commit to MX Device [%(name)s], "
                          "details %(err)s"),
                      {'name': obj_site.netconf_host, 'err': err})
        except Exception as err:
            LOG.error(_LE("Failed to edit[%(action)s] EVPN Type5 Static Route "
                          "for L3VPN DCI, details: %(err)s"),
                      {'action': action, 'err': err})
