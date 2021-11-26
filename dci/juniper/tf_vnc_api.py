import pecan
from vnc_api import vnc_api
from vnc_api import exceptions as vnc_api_exceptions

from oslo_log import log

from dci.common.i18n import _LI
from dci.common.i18n import _LE
from dci import objects


LOG = log.getLogger(__name__)


TF_DEFAULT_DOMAIN = 'default-domain'
TF_DEFAULT_PROJECT = 'admin'
TF_DEFAULT_IPAM = 'dci-controller-default-ipam'
TF_DEFAULT_ROUTR_TARGET = '100:100'


class Client(object):
    """Tungsten Fabric client by VNC API Client.
    """

    def __init__(self, site_uuid):
        self.site_uuid = site_uuid
        self.client = None

        if not self.client:
            self.connect()

        # NOTE(fanguiju): Specialized IPAM object.
        self.ipam_o = None
        try:
            self.ipam_o = self.client.network_ipam_read(
                fq_name=[TF_DEFAULT_DOMAIN,
                         TF_DEFAULT_PROJECT,
                         TF_DEFAULT_IPAM])
        except vnc_api_exceptions.NoIdError as err:
            LOG.info(_LI("Init default IPAM [defailt-ipam]"))
            ipam_uuid = self._create_default_ipam_with_user_defined_subnet()
            self.ipam_o = self.client.network_ipam_read(id=ipam_uuid)

    def connect(self):
        context = pecan.request.context
        obj_site = objects.Site.get(context, self.site_uuid)
        self.client = vnc_api.VncApi(
            api_server_host=obj_site.tf_api_server_host,
            tenant_name=TF_DEFAULT_PROJECT,
            username=obj_site.tf_username,
            password=obj_site.tf_password)

    def _get_default_domain_obj(self):
        return self.client.domain_read(fq_name=[TF_DEFAULT_DOMAIN])

    def _get_default_project_obj(self):
        return self.client.project_read(fq_name=[TF_DEFAULT_DOMAIN,
                                                 TF_DEFAULT_PROJECT])

    def _create_default_ipam_with_user_defined_subnet(self):

        project_o = self._get_default_project_obj()

        # Network IPAM Type
        ipam_t = vnc_api.IpamType(ipam_method='dhcp')

        # Create Network IPAM Object
        ipam_o = vnc_api.NetworkIpam(name=TF_DEFAULT_IPAM,
                                     parent_obj=project_o,
                                     network_ipam_mgmt=ipam_t,
                                     ipam_subnet_method='user-defined-subnet')

        LOG.info(_LI("create default IPAM [%s]"), TF_DEFAULT_IPAM)
        ipam_o = self.client.network_ipam_create(ipam_o)
        return ipam_o

    def _get_subnet_type(self, subnet_cidr):
        prefix, prefix_len = subnet_cidr.split('/')
        subnet_t = vnc_api.SubnetType(ip_prefix=prefix,
                                      ip_prefix_len=int(prefix_len))
        return subnet_t

    def create_virtal_network_with_user_defined_subnet(self, vn_name,
                                                       subnet_cidr):
        project_o = self._get_default_project_obj()

        # Create defined Subnet Type.
        subnet_t = self._get_subnet_type(subnet_cidr)
        ipam_subnet_t = vnc_api.IpamSubnetType(subnet=subnet_t)
        vn_subnet_t = vnc_api.VnSubnetsType(ipam_subnets=[ipam_subnet_t])

        # Virtual Network Type, Setup forwarding mode L2 Only.
        vn_t = vnc_api.VirtualNetworkType(forwarding_mode='l2')

        # Create Virtual Network Object
        LOG.info(_LI("create virtual network [%s]"), vn_name)
        vn_o = vnc_api.VirtualNetwork(name=vn_name,
                                      parent_obj=project_o,
                                      virtual_network_properties=vn_t)
        vn_o.set_network_ipam(ref_obj=self.ipam_o, ref_data=vn_subnet_t)
        self.client.virtual_network_create(vn_o)

    def delete_virtual_network(self, vn_name):
        self.client.virtual_network_delete(
            fq_name=[TF_DEFAULT_DOMAIN, TF_DEFAULT_PROJECT, vn_name])
