import pecan

from jnpr.junos import Device
from jnpr.junos.utils.config import Config

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
            dev = Device(host=obj_site.netconf_host,
                         user=obj_site.netconf_username,
                         password=obj_site.netconf_password).open()
            with Config(dev, mode='private') as cu:
                cu.load(cmd, format='set')
                cu.pdiff()
                cu.commit()
            dev.close()
        except Exception as exc:
            LOG.error(_LE("Failed to edit[%(action)s] EVPN Type5 Static Route "
                          "for L3VPN DCI, details: %(err)s"),
                      {'action': action, 'err': exc.args})
